import logging
import re
from  modules.utils.data_utils import search
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from random import randint
from time import sleep

logging.basicConfig(filename='xe_scrapper.log', level=logging.DEBUG) # encoding='utf-8'

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
        self.driver = None


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

            self.title = soup_lxml.title.string.strip()
            self.price = int(re.findall(r'\d+', soup_lxml.find(class_='price').h2.text)[0])
            self.door = search(self.text, "Πόρτα ασφαλείας")
            self.canopy = search(self.text, "Τέντες")

            if self.description:
                if (self.description.find('πετρέλαιο') != -1) or (self.description.find('πετρελαίου') != -1):
                    self.has_oil = True
            if search(self.text, "Μέσο θέρμανσης:"):
                self.heating = self.text[self.text.index("Μέσο θέρμανσης:") + 2].text
                if self.heating == "Πετρέλαιο" or self.heating == "πετρελαίου":
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


    def set_text(self, soup_html):
        parent = soup_html.find("body").find("ul")  # finding parent <ul> tag
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
        logging.info(f'\nSleeping for {delay} seconds and get web page: {self.property_url} through chrome driver')
        sleep(delay)  # Attempt to avoid scrapping detection
        self.driver.get(self.property_url)

        buttons = self.driver.find_elements_by_class_name('button-property')
        sleep(1)

        actions = ActionChains(self.driver)
        actions.click(buttons[2])
        sleep(1)

        actions.perform()
        elem_list = self.driver.find_elements_by_tag_name('h2') # [7]

        # TODO(SK): false possitives - improve
        if len(elem_list) < 8:
            self.is_estate = True
            logging.debug(f'{self.property_id} len(elem_list) < 8')
            logging.info(f'{self.property_url} has been rejected')

        elif elem_list[7].text == 'Αγγελία ιδιώτη':
            self.is_estate = False
            logging.debug(f'{self.property_url} passes: not estate criterium')

        else:
            self.is_estate = True
            logging.debug(f'{self.property_id} estate')
            logging.info(f'\n{self.property_id} has been rejected\n')


    def validate(self):
        self.check_estate()

        if not self.rejected:
            if self.is_estate:
                logging.debug(f'This house has been published by a real estate. Rejecting...')
                self.rejected = True
            elif self.has_oil:
                logging.debug(f'This house has oil. Rejecting...')
                self.rejected = True
