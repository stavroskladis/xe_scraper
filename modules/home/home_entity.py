import logging
import re
from  modules.utils.data_utils import search
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from random import randint
from time import sleep
import selenium

logging.basicConfig(filename='logs/xe_scrapper.log', level=logging.DEBUG) # encoding='utf-8'
logging.getLogger('charset_normalizer').disabled = True
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)

class Home:

    def __init__(self, property_url):
        self.soup_html = None
        self.soup_lxml = None
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
        self.driver = None


    def set_property_id(self):
        self.property_id = self.property_url.split('/')[6]


    def house_print_info(self):
        logging.info(f'\n\nΠληροφορίες Σπιτιού:')
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
        logging.info(f'Πετρέλαιο: {self.has_oil}\n\n')


    def set_house_info(self):

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
                elif floor_data == 'Ισόγειο, Ημιυπόγειο':
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

            self.title = self.soup_lxml.title.string.strip()
            self.price = int(re.findall(r'\d+', self.soup_lxml.find(class_='price').h2.text)[0])
            self.door = search(self.text, "Πόρτα ασφαλείας")
            self.canopy = search(self.text, "Τέντες")

            if self.description:
                if (self.description.find('πετρέλαιο') != -1) or (self.description.find('πετρελαίου') != -1):
                    self.has_oil = True

            if search(self.text, "Μέσο θέρμανσης:"):
                self.heating = self.text[self.text.index("Μέσο θέρμανσης:") + 2].text

                if self.heating == "Πετρέλαιο" or self.heating == "πετρελαίου" or self.heating.find('Πετρέλαιο') == 0:
                    self.has_oil = True

        except AttributeError as err:
            logging.error(f'Exception while processing house with url: {self.property_url} and id: {self.property_id}')
            logging.error(f'There is no such attribute {err}, {type(err)}')
        except ValueError as err:
            logging.error(f'Exception while processing house with url: {self.property_url} and id: {self.property_id}')
            logging.error(f'Could not convert data to an integer {err}, {type(err)}')
        except BaseException as err:
            logging.error(f'Exception while processing house with url: {self.property_url} and id: {self.property_id}')
            logging.error(f'Unexpected {err}, {type(err)}')
        finally:
            pass


    def set_soup_html(self, soup_html):
        self.soup_html = soup_html

    def set_soup_lxml(self, soup_lxml):
        self.soup_lxml = soup_lxml

    def set_text(self):
        parent = self.soup_html.find("body").find("ul")  # finding parent <ul> tag
        self.text = list(parent.descendants)  # finding all <li> tags


    def check_estate(self):

        DRIVER_PATH = '/usr/local/bin/chromedriver'

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH,options=options)
        self.driver.maximize_window()

        delay = randint(1, 5)
        logging.info(f'\nSleeping for {delay} seconds and getting through chrome driver the web page: \n{self.property_url} ')
        sleep(delay)  # Attempt to avoid scrapping detection
        self.driver.get(self.property_url)
        sleep(1)

        try:
            buttons = self.driver.find_elements_by_class_name('button-property')
        except selenium.common.exceptions.TimeoutException as t_err:
            buttons = []
            logging.error("selenium error: {0}".format(t_err))        
        except BaseException as err:
            logging.error(f'Unexpected {err}, {type(err)}')
        finally:
            pass


        if len(buttons) >= 2:
            
            sleep(1)

            actions = ActionChains(self.driver)
            actions.click(buttons[2])
            sleep(1)

            actions.perform()
            try:
                elem_list = self.driver.find_elements_by_tag_name('h2') # [7]
            except selenium.common.exceptions.TimeoutException as t_err:
                buttons = []
                logging.error("selenium error: {0}".format(t_err))        
            except BaseException as err:
                logging.error(f'Unexpected {err}, {type(err)}')
            finally:
                pass


        # TODO(SK): false possitives - improve
        if self.title.find('Ιδιώτης') != -1:
            self.is_estate = False
            #self.rejected = False

        #elif self.soup_html:
        elif len(self.soup_html.find_all("h2", {"class": "title"})) != 0:
            title = self.soup_html.find_all("h2", {"class": "title"})[0].text
            if (title == 'Αγγελία ιδιώτη'):
                self.is_estate = False
                #self.rejected = False
                logging.info(f'{self.property_url} passes')
                logging.info(f'{self.property_url} not estate (using soup_html)!')


        if len(buttons) >= 2 and not self.is_estate == False:
            
            if len(elem_list) <= 8:
                self.is_estate = True
                logging.info(f'{self.property_id} len(elem_list) <= 8')
                logging.info(f'elem_list = {[l.text for l in elem_list]}')
                logging.info(f'{self.property_url} has been rejected')

            elif elem_list[7].text == 'Αγγελία ιδιώτη':
                self.is_estate = False
                logging.info(f'{self.property_url} passes')
                logging.info(f'{self.property_url} not estate (using soup_html)!')

            else:
                self.is_estate = True
                logging.info(f'{self.property_id} estate')
                logging.info(f'\n{self.property_id} has been rejected\n')


    def validate(self):
        self.check_estate()

        if self.is_estate:
            logging.debug(f'This house has been published by a real estate. Rejecting...')
            self.rejected = True
        elif self.has_oil:
            logging.info(f'This house has oil. Rejecting...')
            self.rejected = True
        else:
            self.rejected = False
            logging.info(f"This house hasn't oil and its not published from a real estate! Accepted!")
    
