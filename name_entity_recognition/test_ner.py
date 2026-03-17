import pytest
from ner import extract_entities


def test_empty_string():
    result = extract_entities("")
    assert result == {}


def test_none_input():
    with pytest.raises(TypeError):
        extract_entities(None)


def test_integer_input():
    with pytest.raises(TypeError):
        extract_entities(123)


def test_list_input():
    with pytest.raises(TypeError):
        extract_entities(["this is a string"])


def test_duplicate_entities():
    text = "Apple Apple Apple in Apple Enterprise Apple HQ Apple Food Apple iPhone"
    result = extract_entities(text)
    assert "ORG" in result, "Expected ORG entities for the provided text"
    apple_count = sum(1 for name in result["ORG"] if "Apple" in name)
    assert apple_count == 1, f"Expected one Apple entry, got {result['ORG']}"


def test_known_entities():
    result = extract_entities("Elon Musk is the CEO of Tesla.")
    assert "Elon Musk" in result.get("PERSON", [])
    assert "Tesla" in result.get("ORG", [])
