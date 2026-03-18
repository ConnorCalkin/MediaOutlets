import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from store import store_article


@pytest.fixture
def valid_article():
    return {
        "article_url": "https://bbc.co.uk/test-article",
        "published_date": "2026-03-17T14:30:00Z",
        "title": "Test Article",
        "body": "This is a test article body.",
        "source_feed": "BBC Business",
        "sentiment": {"polarity": 0.65, "label": "positive"},
        "entities": {"PERSON": ["Elon Musk"], "ORG": ["Tesla"]},
        "keywords": ["Electric Cars"]
    }


# --- Invalid input types ---

def test_none_input():
    with pytest.raises(TypeError):
        store_article(None)


def test_string_input():
    with pytest.raises(TypeError):
        store_article("not a dictionary")


def test_list_input():
    with pytest.raises(TypeError):
        store_article(["article_url", "title"])


def test_integer_input():
    with pytest.raises(TypeError):
        store_article(123)


# --- Missing required fields ---

def test_missing_all_fields():
    with pytest.raises(ValueError, match="Missing required fields:"):
        store_article({})


def test_missing_title():
    with pytest.raises(ValueError, match="title"):
        store_article({
            "article_url": "https://example.com",
            "published_date": "2026-03-17",
            "body": "Some body text.",
            "source_feed": "BBC",
            "sentiment": {"polarity": 0.5, "label": "positive"},
            "entities": {"PERSON": ["Test"]},
            "keywords": ["test"]
        })


def test_missing_sentiment():
    with pytest.raises(ValueError, match="sentiment"):
        store_article({
            "article_url": "https://example.com",
            "published_date": "2026-03-17",
            "title": "Test",
            "body": "Some body text.",
            "source_feed": "BBC",
            "entities": {"PERSON": ["Test"]},
            "keywords": ["test"]
        })


def test_missing_entities():
    with pytest.raises(ValueError, match="entities"):
        store_article({
            "article_url": "https://example.com",
            "published_date": "2026-03-17",
            "title": "Test",
            "body": "Some body text.",
            "source_feed": "BBC",
            "sentiment": {"polarity": 0.5, "label": "positive"},
            "keywords": ["test"]
        })


def test_missing_keywords():
    with pytest.raises(ValueError, match="keywords"):
        store_article({
            "article_url": "https://example.com",
            "published_date": "2026-03-17",
            "title": "Test",
            "body": "Some body text.",
            "source_feed": "BBC",
            "sentiment": {"polarity": 0.5, "label": "positive"},
            "entities": {"PERSON": ["Test"]}
        })


# --- Successful write (new URL) ---

@patch("store.table")
def test_new_article_returns_true(mock_table, valid_article):
    mock_table.put_item.return_value = True
    result = store_article(valid_article)
    assert result is True


@patch("store.table")
def test_new_article_calls_put_item(mock_table, valid_article):
    mock_table.put_item.return_value = True
    store_article(valid_article)
    mock_table.put_item.assert_called_once()


@patch("store.table")
def test_scraped_at_is_added(mock_table, valid_article):
    mock_table.put_item.return_value = True
    store_article(valid_article)
    stored_item = mock_table.put_item.call_args[1]["Item"]
    assert "scraped_at" in stored_item


@patch("store.table")
def test_floats_converted_to_decimal(mock_table, valid_article):
    mock_table.put_item.return_value = True
    store_article(valid_article)
    stored_item = mock_table.put_item.call_args[1]["Item"]
    from decimal import Decimal
    assert stored_item["sentiment"]["polarity"] == Decimal("0.65")


# --- Duplicate URL ---

@patch("store.table")
def test_duplicate_returns_false(mock_table, valid_article):
    mock_table.put_item.side_effect = ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException", "Message": "Duplicate"}},
        "PutItem"
    )
    result = store_article(valid_article)
    assert result is False


@patch("store.table")
def test_duplicate_does_not_raise(mock_table, valid_article):
    mock_table.put_item.side_effect = ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException", "Message": "Duplicate"}},
        "PutItem"
    )
    try:
        store_article(valid_article)
    except Exception:
        pytest.fail("Duplicate article should not raise an exception")


# --- Other AWS errors ---


@patch("store.table")
def test_table_not_found_raises(mock_table, valid_article):
    mock_table.put_item.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}},
        "PutItem"
    )
    with pytest.raises(ClientError):
        store_article(valid_article)
