import re
import smtplib
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
import os
import re
from random import randint
from time import sleep


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
        self.property_url = property_url
        self.property_id = -1
        self.bedroom = -1
        self.bathroom = -1
        self.floor = -1
        self.house_reconstruction = "NA"
        self.building_space = "NA"
        self.compass = "NA"
        self.title = "NA"
        self.price = -1
        self.door = False
        self.canopy = False
        self.heating = "NA"
        self.is_estate = True
        self.description = "NA"
        self.has_oil = False
        self.rejected = True

    def set_property_id(self):
        self.property_id = self.property_url.split('/')[6]

    def house_print_info(self):
        print(f'Ηλεκτρονική Διεύθυνση: {self.property_url}')
        print(f'Αναγνωριστικό: {self.property_id}')
        print(f'Υπνοδωμάτια: {self.bedroom}')
        print(f'Μπάνια: {self.bathroom}')
        print(f'Όροφος: {self.floor}')
        print(f'Έτος ανακαίνισης: {self.house_reconstruction}')
        print(f'Κατάσταση: {self.building_space}')
        print(f'Προσανατολισμός: {self.compass}')
        print(f'Τίτλος: {self.title}')
        print(f'Τιμή: {self.price}')
        print(f'Πόρτα ασφαλείας: {self.door}')
        print(f'Τέντες: {self.canopy}')
        print(f'Θέρμανση: {self.heating}')
        print(f'Μεσίτης: {self.is_estate}')
        print(f'Περιγραφή: {self.description}')
        print(f'Πετρέλαιο: {self.has_oil}')

    def set_house_info(self, soup_html, soup_lxml):

        if search(self.text, "Υπνοδωμάτια:"):
            self.bedroom = int(self.text[self.text.index("Υπνοδωμάτια:") + 2].text)

        if search(self.text, "Μπάνια:"):
            self.bathroom = int(self.text[self.text.index("Μπάνια:") + 2].text)

        floor_data = self.text[self.text.index("Όροφος:") + 2].text
        if type(floor_data) == list and len(floor_data) > 1:
            floor_data = floor_data[0]
        if ((floor_data == 'Ισόγειο') or (floor_data == 'Υπερυψωμένο, Ισόγειο') or (floor_data == 'Υπερυψωμένο')):
            self.floor = 0
        elif floor_data == 'Ημιώροφος':
            self.floor = 1 / 2
        elif floor_data == 'Ημιυπόγειο':
            self.floor = -1 / 2
        else:
            digits = re.findall(r'\d+', floor_data)
            if type(digits) == list and len(digits) > 0:
                digits = digits[0]
            self.floor = int(str(digits))

        if search(self.text, "Έτος ανακαίνισης:"):
            self.house_reconstruction = int(self.text[self.text.index("Έτος ανακαίνισης:") + 2].text)

        if search(self.text, "Κατάσταση:"):
            self.building_space = self.text[self.text.index("Κατάσταση:") + 2].text

        if search(self.text, "Προσανατολισμός:"):
            self.compass = self.text[self.text.index("Προσανατολισμός:") + 2].text

        self.title = soup_lxml.title.string
        self.price = int(re.findall(r'\d+', soup_lxml.find(class_='price').h2.text)[0])
        self.door = search(self.text, "Πόρτα ασφαλείας")
        self.canopy = search(self.text, "Τέντες")

        if search(self.text, "Θέρμανση:"):
            self.heating = self.text[self.text.index("Θέρμανση:") + 2].text

        if self.title.find('Ιδιώτης') != -1:
            self.is_estate = False
        elif len(soup_html.find_all("h2", {"class": "title"})) == 0:
            self.is_estate = True

        if self.description:
            if ((self.description.find('πετρέλαιο') != -1) or (self.description.find('πετρελαίου') != -1)):
                self.has_oil = True
        if search(self.text, "Μέσο θέρμανσης:"):
            self.heating = self.text[self.text.index("Μέσο θέρμανσης:") + 2].text
            if self.heating == "Πετρέλαιο" or self.heating == "πετρελαίου":
                self.has_oil = True

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


def parse_and_filter_homes():
    selected_houses = []
    selected = False

    for h in Homes:
        delay = randint(1, 5)
        print(f'\nProcessing house with id: {h.property_id} (sleeping for {delay} seconds)')
        sleep(delay)

        [soup_html, soup_lxml] = get_soup_objects(h.property_url)

        # find tags and set text
        h.set_text(soup_html)

        h.set_house_info(soup_html, soup_lxml)

        h.validate()

        if not h.rejected:
            h.house_print_info()
            selected_houses.append(h)
            print(f'This house matches out criteria!')
            print(f'Adding it to our database...')
            print(f'Informing you via email...')
        else:
            print(f'{h.property_id} has been rejected')

    return selected_houses


# Fixed query, should be loaded dynamically, raw code should be in function main or another function
query_url = "https://www.xe.gr/property/results?transaction_name=rent&item_type=re_residence&maximum_price=960&minimum_size=57&geo_lat_from=38.0999672763109&geo_lng_from=24.061083822481493&geo_lat_to=37.792875685371634&geo_lng_to=23.530055641375128&sorting=update_desc"
crafted_urls = []
uniq_urls = []
start_page = 0  # Should be 1 at minimum
max_page_num = 1  # upper limit for the web page number to scrapp
links = []

for i in range(start_page, max_page_num):
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
    "keratsini"
    ]

blacklist_areas = unique(blacklist_areas)

cleaned_urls = filter_blacklisted_areas(uniq_urls, blacklist_areas)

Homes = make_homes(cleaned_urls)

selected_houses = parse_and_filter_homes()



