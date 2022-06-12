import requests
from bs4 import BeautifulSoup as bs
import re
from random import randint
from time import sleep
from tqdm import tqdm
import mysql.connector
import logging

logging.basicConfig(filename='xe_scrapper.log', level=logging.DEBUG) # encoding='utf-8'


def insert_variables_into_table(property_id, property_url, bedroom, bathroom, floor, house_reconstruction,
                                building_space, compass, title, price, door, canopy, heating, description, has_oil):
    connection = None
    try:
        # In MySQL 8.0, caching_sha2_password is the default authentication plugin rather than mysql_native_password.
        connection = mysql.connector.connect(host='localhost',
                                             database='xedb',
                                             user='root',
                                             password='dxcfvgbhnjm4567ctfvghj&*(klYFlCnmPzyfvgbh',
                                             auth_plugin='mysql_native_password')

        # Check if property_id exists in our database
        cursor = connection.cursor()
        query = f'SELECT property_id FROM `homes` WHERE property_id = {property_id}'
        res = cursor.execute(query)

        id_found = False
        id_fetched = cursor.fetchone()
        if type(id_fetched) == tuple:
            id_fetched = id_fetched[0]
        if id_fetched == int(property_id):
            logging.debug(f'{property_id} property_id found in db, skipping insert...')
            id_found = True

        # if the house hasn't been already stored in our database, execute insert command
        if not id_found:
            mySql_insert_query = """INSERT INTO homes (property_id, property_url, bedroom, bathroom, floor, 
                                        house_reconstruction, building_space, compass, title, price, door, canopy, heating,
                                        description, has_oil) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

            record = (property_id, property_url, bedroom, bathroom, floor, house_reconstruction, building_space, compass,
                      title, price, door, canopy, heating, description, has_oil)
            cursor.execute(mySql_insert_query, record)
            connection.commit()
            logging.debug("Record inserted successfully into homes table")

    except mysql.connector.Error as error:
        logging.error("Failed to insert into MySQL table {}".format(error))

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logging.debug("MySQL connection is closed")

    return not id_found


# Get unique values
def unique(xlist):
    unique_list = []

    for x in xlist:
        if x not in unique_list:
            unique_list.append(x)

    return unique_list


def search(url_list, keyword):
    for x in range(len(url_list)):
        if url_list[x] == keyword:
            return True
    return False


def filter_blacklisted_areas(urls, blacklisted_areas):
    # Filters based on blacklisted areas

    for url in urls:
        for area in blacklisted_areas:
            if area in url:
                urls.remove(url)
                break  # if blacklisted break the loop
    return urls


class Home:
    def __init__(self, property_url):
        self.text = None
        self.property_url = property_url
        self.property_id = None
        self.bedroom = None
        self.bathroom = None
        self.floor = None
        self.house_reconstruction = None
        self.building_space = None
        self.compass = None
        self.title = None
        self.price = None
        self.door = False
        self.canopy = False
        self.heating = None
        self.is_estate = True
        self.description = None
        self.has_oil = False
        self.rejected = True

    def set_property_id(self):
        self.property_id = self.property_url.split('/')[6]

    def house_print_info(self):
        logging.info(f'Ηλεκτρονική Διεύθυνση: {self.property_url}')
        logging.info(f'Αναγνωριστικό: {self.property_id}')
        logging.info(f'Υπνοδωμάτια: {self.bedroom}')
        logging.info(f'Μπάνια: {self.bathroom}')
        logging.info(f'Όροφος: {self.floor}')
        logging.info(f'Έτος ανακαίνισης: {self.house_reconstruction}')
        logging.info(f'Κατάσταση: {self.building_space}')
        logging.info(f'Προσανατολισμός: {self.compass}')
        logging.info(f'Τίτλος: {self.title}')
        logging.info(f'Τιμή: {self.price}')
        logging.info(f'Πόρτα ασφαλείας: {self.door}')
        logging.info(f'Τέντες: {self.canopy}')
        logging.info(f'Θέρμανση: {self.heating}')
        logging.info(f'Μεσίτης: {self.is_estate}')
        logging.info(f'Περιγραφή: {self.description}')
        logging.info(f'Πετρέλαιο: {self.has_oil}')

    def set_house_info(self, soup_html, soup_lxml):
        try:

            if search(self.text, "Υπνοδωμάτια:"):
                self.bedroom = int(self.text[self.text.index("Υπνοδωμάτια:") + 2].text)

            if search(self.text, "Μπάνια:"):
                self.bathroom = int(self.text[self.text.index("Μπάνια:") + 2].text)

            if search(self.text, "Όροφος:"):
                floor_data = self.text[self.text.index("Όροφος:") + 2].text
                if type(floor_data) == list and len(floor_data) >= 1:
                    floor_data = floor_data[0]
                if (floor_data == 'Ισόγειο') or (floor_data == 'Υπερυψωμένο, Ισόγειο') or (floor_data == 'Υπερυψωμένο'):
                    self.floor = 0
                elif floor_data == 'Ημιώροφος':
                    self.floor = 1 / 2
                elif floor_data == 'Ημιυπόγειο':
                    self.floor = -1 / 2
                elif 'Ισόγειο, Ημιυπόγειο':
                    self.floor = -1 / 2
                else:
                    digits = re.findall(r'\d+', floor_data)
                    if type(digits) == list and len(digits) >= 1:
                        digits = digits[0]
                    self.floor = int(str(digits))

            if search(self.text, "Έτος ανακαίνισης:"):
                self.house_reconstruction = int(self.text[self.text.index("Έτος ανακαίνισης:") + 2].text)

            if search(self.text, "Κατάσταση:"):
                self.building_space = self.text[self.text.index("Κατάσταση:") + 2].text

            if search(self.text, "Προσανατολισμός:"):
                self.compass = self.text[self.text.index("Προσανατολισμός:") + 2].text.strip()

            self.title = soup_lxml.title.string.strip()
            self.price = int(re.findall(r'\d+', soup_lxml.find(class_='price').h2.text)[0])
            self.door = search(self.text, "Πόρτα ασφαλείας")
            self.canopy = search(self.text, "Τέντες")

            if search(self.text, "Θέρμανση:"):
                self.heating = self.text[self.text.index("Θέρμανση:") + 2].text.strip()

            if self.description:
                if (self.description.find('πετρέλαιο') != -1) or (self.description.find('πετρελαίου') != -1):
                    self.has_oil = True
            if search(self.text, "Μέσο θέρμανσης:"):
                self.heating = self.text[self.text.index("Μέσο θέρμανσης:") + 2].text
                if self.heating == "Πετρέλαιο" or self.heating == "πετρελαίου":
                    self.has_oil = True

            if self.title.find('Ιδιώτης') != -1:
                self.is_estate = False
            elif len(soup_html.find_all("h2", {"class": "title"})) == 0:
                self.is_estate = True

        except AttributeError as err:
            logging.error(f'Exception while processing house with url: {self.property_url} and id: {self.property_id}')
            logging.error(f'There is no such attribute {err}, {type(err)}')
            self.rejected = True
            pass
        except BaseException as err:
            logging.error(f'Exception while processing house with url: {self.property_url} and id: {self.property_id}')
            logging.error(f'Unexpected {err}, {type(err)}')
            self.rejected = True
            pass

    def set_text(self, soup_html):
        parent = soup_html.find("body").find("ul")  # finding parent <ul> tag
        self.text = list(parent.descendants)  # finding all <li> tags

    def validate(self):
        if not self.has_oil and not self.is_estate:
            self.rejected = False


def make_homes(urls):
    Homes = []

    for j in range(0, len(urls)):
        Homes.append(Home(urls[j]))
        Homes[j].set_property_id()

    return Homes


def get_soup_objects(url):
    # creating requests object
    html = requests.get(url).content

    # creating soup objects
    soup_html = bs(html, 'html.parser')
    soup_lxml = bs(html, 'lxml')

    return [soup_html, soup_lxml]


def parse_and_filter_homes(homes):
    selected_houses = []

    hbar = tqdm([h for h in homes])
    for h in hbar:
        delay = randint(1, 5)
        sleep(delay)
        hbar.set_description("Processing home with id: %s" % h.property_id)

        logging.info(f'Processing house with id: {h.property_id},\n url: {h.property_id}\n'
                     f'(sleeping for {delay} seconds)\n')

        [soup_html, soup_lxml] = get_soup_objects(h.property_url)

        # find tags and set text
        h.set_text(soup_html)

        h.set_house_info(soup_html, soup_lxml)

        h.validate()

        if not h.rejected:
            h.house_print_info()
            selected_houses.append(h)
            logging.debug(f'This house matches our criteria, trying to add it to our database...')
        else:
            logging.info(f'{h.property_id} has been rejected')

    return selected_houses


def main():
    # Fixed query, should be loaded dynamically, raw code should be in function main or another function
    query_url = "https://www.xe.gr/property/results?transaction_name=rent&item_type=re_residence&maximum_price=960" \
                "&minimum_size=57&geo_lat_from=38.0999672763109&geo_lng_from=24.061083822481493&geo_lat_to=37" \
                ".792875685371634&geo_lng_to=23.530055641375128&sorting=update_desc "

    crafted_urls = []
    start_page = 0  # Should be 1 at minimum
    max_page_num = 50  # upper limit for the web page number to scrap
    links = []

    pgbar = tqdm(range(start_page, max_page_num))
    for i in pgbar:
        delay = randint(1, 5)
        logging.info(f'\nGetting page: {i + 1}, sleeping for {delay} seconds)')
        pgbar.set_description("Getting page: %s" % str(i + 1))
        sleep(delay)

        crafted_urls.append(query_url + "&page=" + str(i + 1))
        soup = bs(requests.get(crafted_urls[i]).content, 'lxml')

        for a_tag in soup.select('a[href*="enoikiaseis-katoikion"]'):
            links.append(a_tag['href'])

        links = links[:-15]

    uniq_urls = unique(links)

    # Should be loaded dynamically
    blacklist_areas = [
        "nosokomeio-paidwn",
        "athhna-plateia-amerikhs",
        "vyrwnas",
        "zwgrafoy-kentro",
        "nosokomeio-paidwn",
        "athhna-koyntoyriwtika",
        "athhna-kynosargoys",
        "galatsi",
        "porto-rafth",
        "pagkrati",
        "ippokratoys",
        "ilion",
        "liosia",
        "keratsini",
        "artemis"
    ]

    blacklist_areas = unique(blacklist_areas)

    cleaned_urls = filter_blacklisted_areas(uniq_urls, blacklist_areas)

    homes = make_homes(cleaned_urls)

    selected_houses = parse_and_filter_homes(homes)

    logging.info(f'\n{len(homes) - len(selected_houses)} houses have been rejected based on your criteria and '
                 f'{len(selected_houses)} houses have been selected:')

    new_homes = []
    for h in selected_houses:
        inserted = insert_variables_into_table(h.property_id, h.property_url, h.bedroom, h.bathroom, h.floor,
                                               h.house_reconstruction, h.building_space, h.compass, h.title, h.price,
                                               h.door, h.canopy, h.heating, h.description, h.has_oil)
        if inserted:
            new_homes.append(h)

    new_homes_len = len(new_homes)
    print(f'\n\n{new_homes_len} new houses found\n')
    for nh in new_homes:
        print(nh.property_url)


if __name__ == "__main__":
    main()
