import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from time import sleep
from random import randint
import logging

logging.basicConfig(filename='xe_scrapper.log', level=logging.DEBUG) # encoding='utf-8'


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

        logging.info(f'Processing house with id: {h.property_id} and url: {h.property_url}')
        logging.info(f'Sleeping for {delay} seconds...')

        [soup_html, soup_lxml] = get_soup_objects(h.property_url)

        # find tags and set text
        h.set_text(soup_html)

        h.set_house_info(soup_html, soup_lxml)

        h.validate()

        if not h.rejected:
            h.house_print_info()
            selected_houses.append(h)
            logging.debug(f'This house matches our criteria (to be add it to our database)...')
        else:
            logging.info(f'{h.property_id} has been rejected')

    return selected_houses
