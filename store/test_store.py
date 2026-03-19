import pytest
from unittest.mock import patch
from botocore.exceptions import ClientError
from store import store_article, get_rows_from_article


@pytest.fixture
def valid_article():
    return {
        "article_url": "https://bbc.co.uk/test-article",
        "published_date": "2026-03-17T14:30:00Z",
        "title": "Test Article",
        "source": "BBC Business",
        "body": "This is a test article body.",
        "sentiment": {"polarity": 0.65, "label": "positive"},
        "entities": {"PERSON": ["Elon Musk"], "ORG": ["Tesla"]},
        "keywords": ["Electric Cars"]
    }


@pytest.fixture
def valid_article_2():
    return {
        "article_url": "https://bbc.co.uk/test-article-2",
        "published_date": "2026-03-17T14:30:00Z",
        "title": "Test Article 2",
        "body": "This is a test article body.",
        "source": "BBC Business",
        "sentiment": {"polarity": 0.65, "label": "positive"},
        "entities": {"PERSON": ["Elon Musk", "Test Person"], "ORG": ["Tesla"]},
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
            "source": "BBC",
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
            "source": "BBC",
            "entities": {"PERSON": ["Test"]},
            "keywords": ["test"]
        })


def test_missing_entities():
    with pytest.raises(ValueError, match="entities"):
        store_article({
            "article_url": "https://example.com",
            "published_date": "2026-03-17",
            "title": "Test",
            "source": "BBC",
            "sentiment": {"polarity": 0.5, "label": "positive"},
            "keywords": ["test"]
        })


def test_missing_keywords():
    with pytest.raises(ValueError, match="keywords"):
        store_article({
            "article_url": "https://example.com",
            "published_date": "2026-03-17",
            "title": "Test",
            "source": "BBC",
            "sentiment": {"polarity": 0.5, "label": "positive"},
            "entities": {"PERSON": ["Test"]}
        })


# --- Successful write (new URL) ---

@patch("store.table")
def test_new_article_returns_none(mock_table, valid_article):
    mock_table.put_item.return_value = True
    result = store_article(valid_article)
    assert result is None


# --- Other AWS errors ---


@patch("store.table")
def test_table_not_found_raises(mock_table, valid_article):
    mock_table.put_item.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}},
        "PutItem"
    )
    with pytest.raises(ClientError):
        store_article(valid_article)

# --- get_rows_from_article tests ---


def test_get_rows_from_article(valid_article):
    rows = get_rows_from_article(valid_article)
    assert isinstance(rows, list)
    assert len(rows) > 0
    main_row = rows[0]
    assert main_row["title"] == valid_article["title"]
    assert main_row["published_date"] == valid_article["published_date"]
    assert main_row["source"] == valid_article["source"]
    assert {
        "pk": f"entity#Elon Musk",
        "sk": valid_article["article_url"],
        "type": "PERSON"} in rows
    assert {
        "pk": f"entity#Tesla",
        "sk": valid_article["article_url"],
        "type": "ORG"} in rows
    assert {
        "pk": f"keyword#Electric Cars",
        "sk": valid_article["article_url"]} in rows


def test_get_rows_from_article_no_entities_keywords():
    article = {
        "article_url": "https://bbc.co.uk/test-article",
        "published_date": "2026-03-17T14:30:00Z",
        "title": "Test Article",
        "body": "This is a test article body.",
        "source": "BBC Business",
        "sentiment": {"polarity": 0.65, "label": "positive"},
        "entities": {},
        "keywords": []
    }
    rows = get_rows_from_article(article)
    assert isinstance(rows, list)
    assert len(rows) == 1  # Only the main row should be created
    main_row = rows[0]
    assert main_row["title"] == article["title"]
    assert main_row["published_date"] == article["published_date"]
    assert main_row["source"] == article["source"]


def test_get_rows_from_article_multiple_entities_keywords(valid_article_2):
    rows = get_rows_from_article(valid_article_2)
    assert isinstance(rows, list)
    assert len(rows) == 5  # Main row + 2 entities + 1 keyword
    main_row = rows[0]
    assert main_row["title"] == valid_article_2["title"]
    assert main_row["published_date"] == valid_article_2["published_date"]
    assert main_row["source"] == valid_article_2["source"]
    assert {
        "pk": f"entity#Elon Musk",
        "sk": valid_article_2["article_url"],
        "type": "PERSON"} in rows
    assert {
        "pk": f"entity#Test Person",
        "sk": valid_article_2["article_url"],
        "type": "PERSON"} in rows
    assert {
        "pk": f"entity#Tesla",
        "sk": valid_article_2["article_url"],
        "type": "ORG"} in rows
    assert {
        "pk": f"keyword#Electric Cars",
        "sk": valid_article_2["article_url"]} in rows
