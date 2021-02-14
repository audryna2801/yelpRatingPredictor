import urllib.parse
import requests
import os
import bs4
import urllib3
import certifi
import json
import csv
import re
import time
import random

# Utility functions
MAIN_URL = "https://www.yelp.com"


def read_url(my_url):
    '''
    Loads html from url. Returns result or "" if the read
    fails.
    '''

    pm = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    return pm.urlopen(url=my_url, method="GET").data


def is_absolute_url(url):
    '''
    Is url an absolute URL?
    '''
    if url == "":
        return False
    return urllib.parse.urlparse(url).netloc != ""


def convert_if_relative_url(new_url, main_url=MAIN_URL):
    '''
    Attempt to determine whether new_url is a relative URL and if so,
    use current_url to determine the path and create a new absolute
    URL.  Will add the protocol, if that is all that is missing.

    Inputs:
        new_url: the path to the restaurants
        main_url: absolute URL

    Outputs:
        new absolute URL or None, if cannot determine that
        new_url is a relative URL.

    Examples:
        convert_if_relative_url("/biz/girl-and-the-goat-chicago", "https://www.yelp.com") yields
            'https://www.yelp.com/biz/girl-and-the-goat-chicago'
    '''
    if new_url == "" or not is_absolute_url(main_url):
        return None

    if is_absolute_url(new_url):
        return new_url

    parsed_url = urllib.parse.urlparse(new_url)
    path_parts = parsed_url.path.split("/")

    if len(path_parts) == 0:
        return None

    ext = path_parts[0][-4:]
    if ext in [".edu", ".org", ".com", ".net"]:
        return "http://" + new_url
    else:
        return urllib.parse.urljoin(main_url, new_url)


# crawling and scraping functions
def get_links_from_page(url):
    '''

    Returns:
        set of restaurant links from the page
    '''
    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    all_tags = soup.find_all("a", href=True)
    all_links = [tag.get("href") for tag in all_tags]
    good_links = {convert_if_relative_url(link) for link in all_links if link.startswith(
        '/biz') and ("?" not in link)}

    return good_links


def get_reviews_from_page(url, writer):
    '''

    Returns:
        None, modifies the csv file in place
    '''
    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    tag = soup.find("script", type="application/ld+json")

    # skips page if tag cannot be found
    if not tag:
        print('failure at page' + str(url))
        return None

    print('success at page' + str(url))

    json_object = json.loads(tag.contents[0])
    reviews = json_object["review"]

    for review in reviews:
        rating = review['reviewRating']["ratingValue"]
        text = review["description"]
        row = [rating, text]
        writer.writerow(row)


def get_total_reviews(soup):
    '''

    Returns: 
        (int) total number reviews for a restaurant
    '''
    tag = soup.find("script", type="application/ld+json")

    if not tag:
        return None

    json_object = json.loads(tag.contents[0])
    total_reviews = json_object["aggregateRating"]['reviewCount']

    return total_reviews


def crawl_resto(url, writer):
    '''

    Returns:
        None, modifies the csv file in place
    '''
    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    total_reviews = get_total_reviews(soup)

    if not total_reviews:
        print('failure at this restaurant ' + str(url))
        return None

    print('sucess at this restaurant' + str(url))

    review_pages = []

    # Each page has 20 reviews, so we increment by 20
    for i in range(0, total_reviews, 20):
        review_pages.append(url + "?start=" + str(i))

    for review_page in review_pages:
        get_reviews_from_page(review_page, writer)

        # Random sleep to avoid being banned by Yelp
        time.sleep(random.randint(1, 3))


def get_total_restos(soup):
    '''

    Returns:
        (int) number of restaurants in the city
    '''
    total_restos_tag = soup.find(
        "span", class_="text__09f24__1RhSS text-color--black-extra-light__09f24__2ZRGr text-align--left__09f24__ceIWW")
    total_restos_str = total_restos_tag.text
    total_restos_page = int(re.search(r'of (\d+)', total_restos_str)[1])

    # Each page has 10 restaurants, so we multiply number of pages * 10
    return total_restos_page * 10


def crawl_city(url):
    '''

    Returns: 
        list of restaurant links in that city
    '''

    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    total_restos = get_total_restos(soup)
    resto_pages = []

    # Each page has 10 restaurants, so we increment by 10
    for i in range(0, total_restos, 10):
        resto_pages.append(url + "&start=" + str(i))

    city_restos = []
    for resto_page in resto_pages:
        city_restos += get_links_from_page(resto_page)

    return city_restos


def crawl_and_scrape(resto_lists_csv="all_restos_lst.csv", scraped_dir="scraped_data/"):
    '''

    Returns:
        None, writes the csv file in place
    '''
    with open(resto_lists_csv, newline='') as f:
        reader = csv.reader(f)
        resto_list = list(reader)

    for i, resto in enumerate(resto_list):
        resto_csv = scraped_dir + str(i) + ".csv"
        print("crawling this url" + " " + resto[0])
        with open(resto_csv, "w") as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(["Rating", "Text"])
            crawl_resto(resto[0].strip("'"), csvwriter)
        # Random sleep to avoid being banned by Yelp
        time.sleep(random.randint(1, 3))
