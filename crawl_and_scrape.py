import urllib.parse
import requests
import os
import bs4
import urllib3
import certifi
import json
import csv

# utility functions
MAIN_URL = "https://www.yelp.com"


def read_url(my_url):
    '''
    Loads html from url. Returns result or "" if the read
    fails.
    '''

    pm = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())
    try:
        return pm.urlopen(url=my_url, method="GET").data
    except Exception:
        print("read failed: " + request.url)
        return ""


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


def get_links_from_page(html):
    '''

    Returns:
        set of restaurant links from the page
    '''

    soup = bs4.BeautifulSoup(html)
    all_tags = soup.find_all("a", href=True)
    all_links = [tag.get("href") for tag in all_tags]
    good_links = {link for link in all_links if link.startswith(
        '/biz') and "?" not in link}

    return good_links


def get_reviews_from_page(html):
    soup = bs4.BeautifulSoup(html)
    tag = soup.find("script", type="application/ld+json")
    json_object = json.loads(tag.contents[0])
    reviews = json_object["review"]
    rows = []

    for review in reviews:
        rating = review['reviewRating']["ratingValue"]
        text = review["description"]
        row = [rating, text]
        rows.append(row)

    return rows


def crawl_and_scrape():
    starting_url = "https://www.yelp.com/search?find_desc=&find_loc=Chicago%2C+IL"
    html = read_url(starting_url)

    with open("reviews.csv", "w") as f:
        writer = csv.writer(f)
    pass
