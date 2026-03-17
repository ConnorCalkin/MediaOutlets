from parsing import get_article_html_from_rss
from scraping import get_body_text
import logging


def get_article_text_from_rss(url: str) -> iter[str]:
    '''Fetches the RSS feed from the specified URL and returns a list of article text.'''
    for article_html in get_article_html_from_rss(url):
        yield get_body_text(article_html)


if __name__ == "__main__":
    url = "https://www.ok.co.uk/?service=rss"
    for article_text in get_article_text_from_rss(url):
        continue
