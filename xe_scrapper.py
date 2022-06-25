from bs4 import BeautifulSoup as bs
import requests
from random import randint
from time import sleep
from tqdm import tqdm
from time import sleep
from modules.db.querries import insert_variables_into_table
from modules.home.home_entity import Home
from modules.utils.data_utils import unique, filter_blacklisted_areas
from modules.utils.parse_utils import parse_and_filter_homes
from modules.utils.home_utils import make_homes
import logging

logging.basicConfig(filename='xe_scrapper.log', level=logging.DEBUG) # encoding='utf-8'


def main():
    # Fixed query, should be loaded dynamically, raw code should be in function main or another function
    query_url = "https://www.xe.gr/property/results?transaction_name=rent&item_type=re_residence&maximum_price=960" \
                "&minimum_size=57&geo_lat_from=38.0999672763109&geo_lng_from=24.061083822481493&geo_lat_to=37" \
                ".792875685371634&geo_lng_to=23.530055641375128&sorting=update_desc "

    crafted_urls = []
    start_page = 0  # Should be 1 at minimum
    max_page_num = 20  # upper limit for the web page number to scrap
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
    shbar = tqdm([sh for sh in selected_houses])
    for sh in shbar:
        inserted = insert_variables_into_table(sh.property_id, sh.property_url, sh.bedroom, sh.bathroom, sh.floor,
                                               sh.house_reconstruction, sh.building_space, sh.compass, sh.title,
                                               sh.price, sh.door, sh.canopy, sh.heating, sh.description, sh.has_oil)
        shbar.set_description("Search db for: %s" % sh.property_id)
        if inserted:
            new_homes.append(sh)
            shbar.set_description("Inserted to db: %s" % sh.property_id)
        else:
            shbar.set_description("House exists in db: %s" % sh.property_id)

    new_homes_len = len(new_homes)
    print(f'\n\n{new_homes_len} new houses found\n')
    for nh in new_homes:
        print(nh.property_url)


if __name__ == "__main__":
    main()
