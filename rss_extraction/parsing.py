import logging
import requests
import xml.etree.ElementTree as ET
from newspaper import Article

logger = logging.getLogger("scraping")


def get_articles_from_rss(url: str):
    """
    Fetches an RSS feed and yields enriched article dictionaries.
    """
    logger.info("Fetching RSS feed: %s", url)

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch RSS feed: {url} (status {response.status_code})")

    root = ET.fromstring(response.text)
    items = root.findall("channel/item")

    logger.info("Found %d articles in feed", len(items))

    for item in items:
        link = item.find("link")
        if link is None or not link.text:
            logger.warning("Skipping article with no URL")
            continue

        logger.info("Processing article: %s", link.text)

        article_data = get_article_data(link.text)
        article_data["published_date"] = item.find(
            "pubDate").text if item.find("pubDate") is not None else None
        yield article_data


def get_article_data(url: str) -> dict:
    """
    Downloads and extracts article data from a given URL using newspaper3k.
    Returns a dictionary containing the article's title, URL, body text, and published date.
    """
    article = Article(url)
    article.download()
    article.parse()
    return {
        "title": article.title,
        "article_url": url,
        "body": article.text,
        "source": article.source_url
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    for article in get_articles_from_rss("https://feeds.bbci.co.uk/news/business/rss.xml"):
        print(f"Title: {article['title']}")
        print(f"Published: {article['published_date']}")
        print(f"Body: {article['body'][:200]}...\n")
        print(f"URL: {article['article_url']}\n")
        print(f'Source: {article["source"]}\n')
        break
