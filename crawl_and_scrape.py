import urllib.parse
import requests
import os
import bs4
import urllib3
import certifi
import json
import csv
import re

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
        '/biz') and "?" not in link}

    return good_links


def get_reviews_from_page(url):
    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
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


def get_total_reviews(soup):
    total_reviews_tag = soup.find(
        "span", class_="text__373c0__2Kxyz text-color--white__373c0__22aE8 text-align--left__373c0__2XGa- text-weight--semibold__373c0__2l0fe text-size--large__373c0__3t60B")
    total_reviews_str = total_reviews_tag.text
    total_reviews = int(re.search('\d+', total_reviews_str).group())
    return total_reviews


def crawl_resto(url):
    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    total_reviews = get_total_reviews(soup)
    review_pages = []

    # Each page has 20 reviews, so we increment by 20
    for i in range(0, total_reviews, 20):
        review_pages.append(url + "?start=" + str(i))

    resto_reviews = []
    for review_page in review_pages:
        resto_reviews += get_reviews_from_page(review_page)

    return resto_reviews


def get_total_restos_page(soup):
    total_restos_tag = soup.find(
        "span", class_="text__09f24__1RhSS text-color--black-extra-light__09f24__2ZRGr text-align--left__09f24__ceIWW")
    total_restos_str = total_restos_tag.text
    total_restos_page = int(re.search(r'of (\d+)', total_restos_str)[1])

    return total_restos_page


def crawl_city(url):
    html = read_url(url)
    soup = bs4.BeautifulSoup(html, "lxml")
    total_restos_page = get_total_restos_page(soup)
    resto_pages = []

    # Each page has 10 restaurants, so we increment by 10
    for i in range(0, total_restos_page * 10, 10):
        resto_pages.append(url + "&start=" + str(i))

    city_restos = []
    for resto_page in resto_pages:
        city_restos += get_links_from_page(resto_page)

    return city_restos


def crawl_and_scrape():
    city_url = "https://www.yelp.com/search?find_desc=&find_loc=Chicago%2C%20IL&ns=1"
    city_restos = crawl_city(city_url)
    with open("reviews.csv", "w") as f:
        writer = csv.writer(f)

    for resto in city_restos:
        reviews = crawl_resto(resto)
        writer.writerows(reviews)
