from decimal import Decimal
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger("store")

dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")
table = dynamodb.Table("c22-dashboard-divas-db")


def convert_floats(data):
    """
    Recursively converts float values to Decimal for DynamoDB compatibility.
    """
    if isinstance(data, float):
        return Decimal(str(data))
    if isinstance(data, dict):
        return {key: convert_floats(value) for key, value in data.items()}
    if isinstance(data, list):
        return [convert_floats(item) for item in data]
    return data


def validate_article(article) -> bool:
    """
    Validates that the article contains all required fields.
    """

    # Check that the article is a dictionary
    if not isinstance(article, dict):
        raise TypeError("Article must be a dictionary")

    # Validate required fields and primary key format based on the row type definition
    required_fields = ["article_url", "published_date", "title",
                       "body", "source", "sentiment", "entities", "keywords"]
    missing_fields = [
        field for field in required_fields if field not in article]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

    return True


def get_rows_from_article(article: dict) -> list[dict]:
    '''Converts an enriched article dictionary into a list of rows to be stored in DynamoDB.'''
    rows = []
    # main row with article metadata and sentiment analysis results
    rows.append({
        "pk": article["article_url"],
        "sk": "metadata",
        "published_date": article["published_date"],
        "title": article["title"],
        "body": article["body"],
        "source": article["source"],
        "sentiment": article["sentiment"],
        "scraped_at": article.get("scraped_at", datetime.now().isoformat())
    })

    # additional rows for each entity and keyword, linking back to the main article row via the article_url
    for entity_type, entity in article["entities"].items():
        rows.append({
            "pk": f"entity#{entity}",
            "sk": article["article_url"],
            "type": entity_type
        })
    for keyword in article["keywords"]:
        rows.append({
            "pk": f"keyword#{keyword}",
            "sk": article["article_url"]
        })
    return rows


def is_duplicate(article_url: str) -> bool:
    '''Checks if an article with the given URL already exists in the database.'''
    try:
        response = table.get_item(
            Key={
                "pk": article_url,
                "sk": "metadata"
            }
        )
        if "Item" in response:
            logger.warning(f"Duplicate article found: {article_url}")
            return True
        return False
    except ClientError as e:
        logger.error(f"Error checking for duplicate article: {e}")
        raise e


def store_article(article_data: dict) -> None:

    validate_article(article_data)

    # Work on a copy to avoid mutating the caller-provided dictionary.
    enriched_article_data = dict(article_data)

    enriched_article_data["scraped_at"] = datetime.now().isoformat()
    enriched_article_data = convert_floats(enriched_article_data)

    if is_duplicate(enriched_article_data["article_url"]):
        logger.error(
            f"Article with URL {enriched_article_data['article_url']} already exists in the database.")
        raise ValueError(
            f"Article with URL {enriched_article_data['article_url']} already exists in the database.")

    logger.info(f"Storing article: {enriched_article_data['article_url']}")

    # Add rows to database
    rows = get_rows_from_article(enriched_article_data)
    for row in rows:
        logger.info("Storing row with PK: %s, SK: %s", row["pk"], row["sk"])
        table.put_item(
            Item=row,
        )
        logger.info(f"Successfully stored row: {row['pk']} - {row['sk']}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    result = store_article({
        "article_url": "https://bbc.co.uk/test-article2",
        "published_date": "2026-03-17T14:30:00Z",
        "title": "Test Article",
        "body": "This is a test article body.",
        "source": "BBC Business",
        "sentiment": {"polarity": 0.65, "label": "positive"},
        "entities": {"PERSON": ["Elon Musk"], "ORG": ["Tesla"]},
        "keywords": ["Electric Cars"]
    })
