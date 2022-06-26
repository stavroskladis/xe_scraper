import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from time import sleep
from random import randint
import logging

logging.basicConfig(filename='logs/xe_scrapper.log', level=logging.INFO) # encoding='utf-8'
logging.getLogger('charset_normalizer').disabled = True
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)


def get_soup_objects(url):
    # creating requests object
    html = requests.get(url).content

    # creating soup objects
    soup_html = bs(html, 'html.parser')
    soup_lxml = bs(html, 'lxml')

    return [soup_html, soup_lxml]


def parse_and_filter_homes(homes):
    selected_houses = []
    rejected_houses = []

    hbar = tqdm([h for h in homes])

    counter = 0

    for h in hbar:

        counter += 1
        if counter <= 10:
             continue
        elif counter > 20:
            break

        delay = randint(1, 5)
        sleep(delay)
        hbar.set_description("Processing home with id: %s" % h.property_id)

        logging.info(f'\n\n---------------------------------------------------------------')
        logging.info(f'Processing house with id: {h.property_id} and url: {h.property_url}')
        logging.info(f'Sleeping for {delay} seconds...')

        try:
            [soup_html, soup_lxml] = get_soup_objects(h.property_url)
            if soup_html:
                h.set_soup_html(soup_html)
            if soup_lxml:
                h.set_soup_lxml(soup_lxml)
                h.set_text()  # find tags and set text


            if h.soup_html and soup_html:
                h.set_house_info()
                h.validate()
            else:
                h.rejected = True
                logging.info(f'This house {h.property_url} has been rejected because no soup_html was found!')


            if not h.rejected:
                h.house_print_info()
                selected_houses.append(h)
                logging.info(f'This house matches our criteria (to be add it to our database)...')
            else:
                rejected_houses.append(h)  # for debugging reasons
                logging.info(f'{h.property_id} has been rejected')
                logging.info(f'-------------------------------------------------------------------------')
        
        except BaseException as err:
            logging.error(f'parse_and_filter_homes(): Unexpected {err}, {type(err)}')

    return selected_houses
