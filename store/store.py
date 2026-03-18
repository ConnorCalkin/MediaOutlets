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


def store_article(article_data):
    """
    Write an enriched article record to the DynamoDB table.

    Returns
    -------
    bool
        True if the article was stored successfully.
        False if the article already exists and the write was skipped
        due to the conditional check (duplicate article).

    Raises
    ------
    TypeError
        If ``article_data`` is not a dictionary.
    ValueError
        If one or more required fields are missing from ``article_data``.
    botocore.exceptions.ClientError
        If a non-duplicate AWS DynamoDB error occurs (for example,
        permissions issues, throttling, or table not found).
    """
    if not isinstance(article_data, dict):
        raise TypeError("Input must be a dictionary")

    required_fields = ["article_url", "published_date",
                       "title", "body", "source_feed", "sentiment", "entities", "keywords"]
    missing = [field for field in required_fields if field not in article_data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    article_data["scraped_at"] = datetime.now().isoformat()
    article_data = convert_floats(article_data)

    logger.info("Storing article: %s", article_data["article_url"])

    try:
        # Only write if no item with this article_url exists already.
        # Without this condition, put_item would silently overwrite duplicates.
        table.put_item(
            Item=article_data,
            ConditionExpression="attribute_not_exists(article_url)"
        )
        logger.info("Successfully stored article: %s",
                    article_data["article_url"])
        return True

    except ClientError as e:
        # Gracefully handle the case where the article already exists (duplicate).
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            logger.warning("Duplicate article, skipping: %s",
                           article_data["article_url"])
            return False
        else:
            # Any other AWS error (permissions, throttling, table not found, etc.)
            logger.error("Failed to store article: %s - %s",
                         article_data["article_url"], str(e))
            raise e


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
        "source_feed": "BBC Business",
        "sentiment": {"polarity": 0.65, "label": "positive"},
        "entities": {"PERSON": ["Elon Musk"], "ORG": ["Tesla"]},
        "keywords": ["Electric Cars"]
    })
