from parsing import get_articles_from_rss
from extractkeywords import extract_keywords_spacy
from ner import extract_entities
from sentiment_analysis import analyse_sentiment
from ingest import ingest_article
from store import store_article
import logging

print("import works")

RSS_FEED = 'https://www.ok.co.uk/?service=rss'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_enriched_article(article: dict) -> dict:
    '''
    Add the enriched information to the article dictionary
    1. Extract keywords
    2. Extract named entities
    3. Analyse sentiment
    '''
    return {
        'title': article['title'],
        'published_date': article['published'],
        'article_url': article['url'],
        'keywords': extract_keywords_spacy(article['body']),
        'entities': extract_entities(article['body']),
        'sentiment': analyse_sentiment(article['body']),
        'source': RSS_FEED
    }


def ingest_wrapper(article: dict) -> None:
    '''Wrapper around the ingest_article function to handle exceptions and log errors'''
    logger.info(f"Starting ingestion for article: {article['url']}")
    try:
        ingest_article(
            title=article['title'],
            url=article['url'],
            text=article['body'],
            source=RSS_FEED
        )
        logger.info(f"Successfully ingested article: {article['article_url']}")
    except Exception as e:
        logger.error(f"Error ingesting article {article['article_url']}: {e}")


def store_wrapper(article: dict) -> None:
    '''Wrapper around the store_article function to handle exceptions and log errors'''
    try:
        store_article(article)
        logger.info(f"Successfully stored article: {article['article_url']}")
    except Exception as e:
        logger.error(f"Error storing article {article['article_url']}: {e}")


def pipeline(event=None, context=None) -> dict:
    '''
    runs the pipeline for the RSS feed, which includes:
    1. Extracting articles from the RSS feed
    2. Enriching the article with keywords, entities and sentiment analysis
    3. Ingesting the enriched article into the vector store
    4. Add enriched articles to database
    '''
    articles = get_articles_from_rss(RSS_FEED)
    for article in articles:
        # ingest articles into chromadb for RAG server
        ingest_wrapper(article)
        # add keywords, entities and sentiment analysis to article dictionary
        enriched_article = get_enriched_article(article)
        # add enriched article to database
        store_wrapper(enriched_article)

    return {
        "statusCode": 200,
        "body": f"Successfully processed articles from RSS feed"
    }


if __name__ == "__main__":
    pipeline()
