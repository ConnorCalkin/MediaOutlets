import requests
import xml.etree.ElementTree as ET
import logging
from scraping import get_body_text
from utils import debug_generator


@debug_generator
def get_url_contents(url: str) -> str:
    '''Fetches the content from the specified URL and returns it as a string.'''
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(
            f"Failed to fetch URL: {url} with status code: {resp.status_code}")
    return resp.text


def get_body_text_from_url(url: str) -> str:
    '''Fetches the content from the specified URL and returns the text content of the article element.'''
    html = get_url_contents(url)
    return get_body_text(html)


def get_articles_from_rss(content: str) -> list[str]:
    '''
    Parses the RSS feed content and returns a list of all link elements.
    All of the articles are stored in an item element
    The children are used to populate the article title, body and published date
    '''
    root = ET.fromstring(content)
    items = root.findall('channel/item')
    for item in items:
        yield {
            'title': item.find('title').text,
            'body': get_body_text_from_url(item.find('link').text),
            'published': item.find('pubDate').text
        }


if __name__ == "__main__":
    rss_content = get_url_contents('https://www.ok.co.uk/?service=rss')
    articles = get_articles_from_rss(rss_content)
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Published: {article['published']}")
        print(f"Body: {article['body']}\n")
        break
