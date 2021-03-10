import urllib.parse
import urllib3
import certifi


MAIN_URL = "https://www.yelp.com"


def read_url(my_url):
    '''
    Load HTML from URL. Return result or empty string if the
    read fails.

    Inputs:
      - my_url (str): URL

    Returns: str
    '''
    pm = urllib3.PoolManager(
        cert_reqs="CERT_REQUIRED",
        ca_certs=certifi.where())

    return pm.urlopen(url=my_url, method="GET").data


def is_absolute_url(url):
    '''
    Determine if a URL is an absolute URL.

    Inputs:
      - url (str): URL

    Returns: Bool
    '''

    if url == "":
        return False
    return urllib.parse.urlparse(url).netloc != ""


def convert_if_relative_url(new_url, main_url=MAIN_URL):
    '''
    Attempt to determine whether new_url is a relative URL and if so,
    use current_url to determine the path and create a new absolute
    URL. Add the protocol, if that is all that is missing.

    Inputs:
      - new_url (str): the path to the restaurants
      - main_url (str): absolute URL

    Returns: str or None

    Examples:
        convert_if_relative_url("/biz/girl-and-the-goat-chicago",
                                "https://www.yelp.com")
        yields "https://www.yelp.com/biz/girl-and-the-goat-chicago"
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
