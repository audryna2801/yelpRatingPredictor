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

    Inputs:
        - my_url (str)

    Returns: the html
    '''

    pm = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    return pm.urlopen(url=my_url, method="GET").data


def is_absolute_url(url):
    '''
    Determines if url is an absolute url

    Inputs:
        - url (str)

    Returns: boolean
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

    Returns:
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


# Crawling and scraping functions
def get_total_reviews(soup, counter):
    '''
    Given a soup object representing a page,
    it will get the total number of reviews to
    help the program determine how many pages of 
    reviews to scrape.

    Inputs:
        - soup (bs4 object)
        - counter (int): if the program gets blocked by Yelp,
            how many times should it try again before giving up
            and skipping (high number corresponds to longer run-time, 
            but less pages being skipped)

    Returns: 
        (int) total number reviews for a restaurant
    '''
    tag = soup.find("script", type="application/ld+json")

    # Tries again if tag cannot be found, number of tries depend on counter
    if not tag:
        for _ in range(counter):
            tag = soup.find("script", type="application/ld+json")
            time.sleep(random.randint(1, 3))
            if tag:
                break
        if not tag:
            return None

    json_object = json.loads(tag.contents[0])
    total_reviews = json_object["aggregateRating"]['reviewCount']

    return total_reviews


def get_reviews_from_page(url, writer, counter):
    '''
    Given a url and csv writer object, writes all the reviews
    from a given page to the csv

    Inputs: 
        - url (str)
        - writer (csv writer object)
        - counter (int): if the program gets blocked by Yelp,
            how many times should it try again before giving up
            and skipping (high number corresponds to longer run-time, 
            but less pages being skipped)

    Returns:
        None, modifies the csv file in place
    '''

    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    tag = soup.find("script", type="application/ld+json")

    # Tries again if tag cannot be found, number of tries depend on counter
    if not tag:
        for _ in range(counter):
            tag = soup.find("script", type="application/ld+json")
            time.sleep(random.randint(1, 3))
            if tag:
                break
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


def crawl_resto(url, writer, counter):
    '''
    Crawls the restaurant and get all reviews from the restaurant

    Inputs:
        - url (str): the url
        - writer (csv writer): the writer object
        - counter (int): if the program gets blocked by Yelp,
            how many times should it try again before giving up
            and skipping (high number corresponds to longer run-time, 
            but less pages being skipped)

    Returns:
        None, modifies the csv file in place
    '''
    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    total_reviews = get_total_reviews(soup, counter)

    if not total_reviews:
        print('failure at this restaurant ' + str(url))
        return None

    print('sucess at this restaurant' + str(url))

    review_pages = []

    # Each page has 20 reviews, so we increment by 20
    for i in range(0, total_reviews, 20):
        review_pages.append(url + "?start=" + str(i))

    for review_page in review_pages:
        get_reviews_from_page(review_page, writer, counter)

        # Random sleep to avoid being banned by Yelp
        time.sleep(random.randint(1, 3))


def get_links_from_page(url):
    '''
    Given a url, scrapes all other urls that refer to restaurant
    home pages and converts it to absolute url

    Inputs: 
        - url (str): the url

    Returns: set of restaurant links from the page
    '''
    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    all_tags = soup.find_all("a", href=True)
    all_links = [tag.get("href") for tag in all_tags]
    good_links = {convert_if_relative_url(link) for link in all_links if link.startswith(
        '/biz') and ("?" not in link)}

    return good_links


def crawl_city(url):
    '''
    Crawls the city and gets all the urls of restaurants
    within that city

    Inputs:
        - url (str): the url

    Returns: 
        list of restaurant links in that city
    '''

    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    # yelp displays 24 pages of reviews for each location
    total_restos = 24
    resto_pages = []

    # Each page has 10 restaurants, so we increment by 10
    for i in range(0, total_restos, 10):
        resto_pages.append(url + "&start=" + str(i))

    city_restos = []
    for resto_page in resto_pages:
        city_restos += get_links_from_page(resto_page)
        # Random sleep to avoid being banned by Yelp
        time.sleep(random.randint(1, 3))

    return city_restos


def crawl_and_scrape(counter=10, city_url="https://www.yelp.com/search?find_desc=&find_loc=Chicago%2C%20IL",
                     csv_repo="scraped_data/"):
    '''
    Crawls the city of Chicago, unless another city url is given,
    and write all reviews from restaurants in that city to a csv file. csv file 
    does not contain headers.

    Inputs:
        - counter (int): if the program gets blocked by Yelp,
            how many times should it try again before giving up
            and skipping (high number corresponds to longer run-time, 
            but less pages being skipped)
        - city_url (str): the yelp url of the city
        - csv_repo (str): the name of the repository to store all scraped data

    Returns:
        None, writes the csv file in place
    '''

    city_restos = crawl_city(city_url)

    for i, resto in enumerate(city_restos):
        filename = csv_repo + str(i) + ".csv"
        with open(filename, "w") as f:
            csvwriter = csv.writer(f)
            crawl_resto(resto, csvwriter, counter)
            # Random sleep to avoid being banned by Yelp
            time.sleep(random.randint(1, 3))
