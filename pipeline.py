from parsing import get_articles_from_rss
from extractkeywords import extract_keywords_spacy
from ner import extract_entities
from sentiment_analysis import analyse_sentiment
from ingest import ingest_article
from store import store_article
import logging
import boto3
import json

RSS_FEEDS = ['https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
             'https://feeds.bbci.co.uk/news/business/rss.xml']
BUCKET_NAME = "c22-dashboard-divas-article-storage"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


s3 = boto3.client("s3", region_name="eu-west-2")


def upload_to_s3(article: dict) -> None:
    """Uploads article body and URL to S3 as a JSON file."""
    key = f"articles/{article['article_url'].replace('https://', '').replace('/', '_')}.json"

    data = {
        "article_url": article["article_url"],
        "body": article["body"]
    }

    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        logger.info("Uploaded to S3: %s", key)
    except Exception as e:
        logger.error("Failed to upload to S3: %s - %s", article["url"], e)


def get_enriched_article(article: dict) -> dict:
    '''
    Add the enriched information to the article dictionary
    1. Extract keywords
    2. Extract named entities
    3. Analyse sentiment
    '''
    return {
        'title': article['title'],
        'published_date': article['published_date'],
        'article_url': article['article_url'],
        'keywords': extract_keywords_spacy(article['body']),
        'entities': extract_entities(article['body']),
        'sentiment': analyse_sentiment(article['body']),
        'source': article['source']
    }


def ingest_wrapper(article: dict) -> None:
    '''Wrapper around the ingest_article function to handle exceptions and log errors'''
    logger.info(f"Starting ingestion for article: {article['url']}")
    try:
        ingest_article(
            title=article['title'],
            url=article['article_url'],
            text=article['body'],
            source=article['source']
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
    runs the pipeline for the RSS feeds, which includes:
    1. Extracting articles from the RSS feeds
    2. Enriching the article with keywords, entities and sentiment analysis
    3. Ingesting the enriched article into the vector store
    4. Add enriched articles to database
    '''
    for feed in RSS_FEEDS:
        logger.info("Processing feed: %s", feed)
        articles = get_articles_from_rss(feed)
        for article in articles:
            upload_to_s3(article)
            # ingest articles into chromadb for RAG server
            ingest_wrapper(article)
            # add keywords, entities and sentiment analysis to article dictionary
            enriched_article = get_enriched_article(article)
            # add enriched article to database
            store_wrapper(enriched_article)

    return {
        "statusCode": 200,
        "body": f"Successfully processed articles from {len(RSS_FEEDS)} RSS feeds"
    }


if __name__ == "__main__":
    pipeline()
