from parsing import get_articles_from_rss
from extractkeywords import extract_keywords_spacy
from ner import extract_entities
from sentiment_analysis import analyse_sentiment
from ingest import ingest_article
import logging

print("import works")

RSS_FEED = 'https://www.ok.co.uk/?service=rss'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_enriched_article(article):
    '''
    Add the enriched information to the article dictionary
    1. Extract keywords
    2. Extract named entities
    3. Analyse sentiment
    '''
    return {
        'title': article['title'],
        'published': article['published'],
        'url': article['url'],
        'keywords': extract_keywords_spacy(article['body']),
        'entities': extract_entities(article['body']),
        'sentiment': analyse_sentiment(article['body'])
    }


def ingest(article) -> None:
    '''Wrapper around the ingest_article function to handle exceptions and log errors'''
    try:
        ingest_article(
            title=article['title'],
            url=article['url'],
            text=article['body'],
            source=RSS_FEED
        )
        logger.info(f"Successfully ingested article: {article['url']}")
    except Exception as e:
        logger.error(f"Error ingesting article {article['url']}: {e}")


def pipeline():
    '''
    runs the pipeline for the RSS feed, which includes:
    1. Extracting articles from the RSS feed
    2. Enriching the article with keywords, entities and sentiment analysis
    3. Ingesting the enriched article into the vector store
    4 TODO: Add enriched articles to database
    '''
    articles = get_articles_from_rss(RSS_FEED)
    for article in articles:
        # ingest articles into chromadb for RAG server
        ingest(article)
        # add keywords, entities and sentiment analysis to article dictionary
        enriched_article = get_enriched_article(article)
        # TODO: Add enriched articles to database


if __name__ == "__main__":
    pipeline()
