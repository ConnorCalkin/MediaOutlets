import requests
import xml.etree.ElementTree as ET
import logging
from utils import debug_generator


@debug_generator
def get_url_contents(url: str) -> str:
    '''Fetches the content from the specified URL and returns it as a string.'''
    resp = requests.get(url)

    if resp.status_code != 200:
        logging.error(
            f"Failed to fetch URL: {url} with status code: {resp.status_code}")
        return ""

    return resp.text


def get_links_from_rss(content: str) -> list[str]:
    '''Parses the RSS feed content and returns a list of all link elements.'''
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        logging.error(f"Failed to parse RSS content: {e}")
        return []
    links = root.findall(".//item/link")
    return [link.text for link in links]


def get_article_html_from_rss(url: str) -> iter[str]:
    '''Fetches the RSS feed from the specified URL and returns a list of article html.'''
    content = get_url_contents(url)
    links = get_links_from_rss(content)
    for link in links:
        yield get_url_contents(link)


if __name__ == "__main__":
    url = "https://www.ok.co.uk/?service=rss"
    for article_html in get_article_html_from_rss(url):
        print(article_html)
        break
