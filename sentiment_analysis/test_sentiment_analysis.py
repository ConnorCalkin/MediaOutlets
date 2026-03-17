import pytest
from sentiment_analysis import analyse_sentiment


# Invalid inputs
def test_none_input():
    with pytest.raises(TypeError):
        analyse_sentiment(None)


def test_integer_input():
    with pytest.raises(TypeError):
        analyse_sentiment(123)


def test_list_input():
    with pytest.raises(TypeError):
        analyse_sentiment(["this is a string"])


# Empty and whitespace
def test_empty_string():
    result = analyse_sentiment("")
    assert result == {"polarity": 0.0, "label": "neutral"}


# Return structure
def test_returns_polarity_and_label():
    result = analyse_sentiment("Some text about a company.")
    assert "polarity" in result
    assert "label" in result


def test_polarity_is_float():
    result = analyse_sentiment("This is a great product.")
    assert isinstance(result["polarity"], float)


def test_label_is_valid():
    result = analyse_sentiment("This is a great product.")
    assert result["label"] in ("positive", "negative", "neutral")


# Positive sentiment
def test_positive_sentiment():
    result = analyse_sentiment(
        "This is an amazing and wonderful achievement for the company.")
    assert result["label"] == "positive"
    assert result["polarity"] > 0.05


# Negative sentiment
def test_negative_sentiment():
    result = analyse_sentiment(
        "This is a terrible disaster that caused widespread damage and suffering.")
    assert result["label"] == "negative"
    assert result["polarity"] < -0.05


# Neutral sentiment
def test_neutral_sentiment():
    result = analyse_sentiment("The company released a statement on Tuesday.")
    assert result["label"] == "neutral"


# Short text
def test_short_text():
    result = analyse_sentiment("Bad.")
    assert isinstance(result["polarity"], float)
    assert result["label"] in ("positive", "negative", "neutral")


# Very long text
def test_long_text():
    long_text = "The company reported strong earnings. " * 10000
    result = analyse_sentiment(long_text)
    assert isinstance(result["polarity"], float)
    assert result["label"] in ("positive", "negative", "neutral")


# Mixed sentiment
def test_mixed_sentiment():
    result = analyse_sentiment(
        "Apple reported record revenue but is facing a major antitrust lawsuit."
    )
    assert isinstance(result["polarity"], float)
    assert result["label"] in ("positive", "negative", "neutral")


# All caps
def test_all_caps_stronger_than_lowercase():
    lower = analyse_sentiment("this is amazing")
    upper = analyse_sentiment("this is AMAZING")
    assert upper["polarity"] >= lower["polarity"]


# Sarcasm limitation
def test_sarcasm_known_limitation():
    result = analyse_sentiment(
        "Oh great, another data breach. What a surprise.")
    # VADER will likely read this as positive due to "great" and "surprise"
    # This test documents the limitation rather than expecting correct behaviour
    assert isinstance(result["polarity"], float)
    assert result["label"] == "positive"
