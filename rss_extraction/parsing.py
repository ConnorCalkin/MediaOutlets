import logging
import requests
import xml.etree.ElementTree as ET
from scraping import get_body_text

logger = logging.getLogger("parsing")


def get_articles_from_rss(url: str) -> list[dict]:
    """
    Fetches an RSS feed and yields enriched article dictionaries.
    For each item in the feed, the article body is downloaded and
    extracted using newspaper3k via the scraping module.
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
        article_url = item.find("link").text
        title = item.find("title").text
        published = item.find("pubDate").text

        logger.info("Processing article: %s", article_url)

        body = get_body_text(article_url)

        yield {
            "title": title,
            "url": article_url,
            "body": body,
            "published": published,
        }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    for article in get_articles_from_rss("https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"):
        print(f"Title: {article['title']}")
        print(f"Published: {article['published']}")
        print(f"Body: {article['body'][:200]}...\n")
        break
