from parsing import get_articles_from_rss
from extractkeywords import extract_keywords_spacy
from ner import extract_entities
from sentiment_analysis import analyse_sentiment
from ingest import ingest_article
import logging

RSS_FEED = 'https://www.ok.co.uk/?service=rss'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_enriched_article(article):
    return {
        'title': article['title'],
        'published': article['published'],
        'url': article['url'],
        'keywords': extract_keywords_spacy(article['body']),
        'entities': extract_entities(article['body']),
        'sentiment': analyse_sentiment(article['body'])
    }


def ingest(article) -> None:
    try:
        ingest_article(
            article_id=article['url'],
            title=article['title'],
            url=article['url'],
            text=article['body'],
            source=RSS_FEED
        )
        logger.info(f"Successfully ingested article: {article['url']}")
    except Exception as e:
        logger.error(f"Error ingesting article {article['url']}: {e}")


def pipeline():
    articles = get_articles_from_rss(RSS_FEED)
    for article in articles:
        ingest(article)
        enriched_article = get_enriched_article(article)
        # TODO: Add enriched articles to database


if __name__ == "__main__":
    pipeline()
