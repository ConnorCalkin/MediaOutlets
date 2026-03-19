from ner import extract_entities, validate_entities
import pytest

# --- extract_entities: Invalid inputs ---


def test_empty_string():
    result = extract_entities("")
    assert result == {}


def test_whitespace_only():
    result = extract_entities("   \n\t  ")
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
    assert "ORG" in result, f"Expected ORG entities for text, got {result}"
    apple_count = sum(1 for name in result.get("ORG", []) if "Apple" in name)
    assert apple_count == 1, f"Expected one Apple entry, got {result.get('ORG', [])}"


def test_known_person():
    result = extract_entities("Elon Musk is the CEO of Tesla.")
    assert "Elon Musk" in result.get("PERSON", [])


def test_known_org():
    result = extract_entities("Elon Musk is the CEO of Tesla.")
    assert "Tesla" in result.get("ORG", [])


def test_no_entities_found():
    result = extract_entities("The weather today is sunny and warm.")
    assert result == {}


def test_only_person_and_org_extracted():
    result = extract_entities(
        "Elon Musk flew from London to Berlin on Monday.")
    assert "GPE" not in result
    assert "DATE" not in result


# --- validate_entities: Word length filter ---

def test_validate_removes_long_entities():
    entities = {
        "ORG": ["Apple", "Debenhams on the Outsunny 4 Pieces Rattan Set"]}
    result = validate_entities(entities)
    assert "Apple" in result["ORG"]
    assert len(result["ORG"]) == 1


def test_validate_keeps_four_word_entity():
    entities = {"ORG": ["Goldman Sachs Investment Bank"]}
    result = validate_entities(entities)
    assert "Goldman Sachs Investment Bank" in result["ORG"]


def test_validate_removes_five_word_entity():
    entities = {"ORG": ["Goldman Sachs Investment Bank Group"]}
    result = validate_entities(entities)
    assert result["ORG"] == []


# --- validate_entities: Single character filter ---

def test_validate_removes_single_character():
    entities = {"PERSON": ["A", "Elon Musk"]}
    result = validate_entities(entities)
    assert "A" not in result["PERSON"]
    assert "Elon Musk" in result["PERSON"]


def test_validate_removes_whitespace_only_entity():
    entities = {"ORG": [" ", "Tesla"]}
    result = validate_entities(entities)
    assert "Tesla" in result["ORG"]
    assert len(result["ORG"]) == 1


# --- validate_entities: PERSON capitalisation ---

def test_validate_removes_lowercase_person():
    entities = {"PERSON": ["Elon Musk", "easter", "jordan"]}
    result = validate_entities(entities)
    assert "Elon Musk" in result["PERSON"]
    assert "easter" not in result["PERSON"]
    assert "jordan" not in result["PERSON"]


def test_validate_keeps_fully_capitalised_person():
    entities = {"PERSON": ["King Abdullah II"]}
    result = validate_entities(entities)
    assert "King Abdullah II" in result["PERSON"]


def test_validate_does_not_capitalise_filter_orgs():
    entities = {"ORG": ["BBC", "amazon"]}
    result = validate_entities(entities)
    assert "amazon" in result["ORG"]


# --- validate_entities: ORG deduplication ---

def test_validate_deduplicates_orgs():
    entities = {"ORG": ["Apple", "Apple Inc.", "Apple Inc"]}
    result = validate_entities(entities)
    assert result["ORG"] == ["Apple"]


def test_validate_keeps_distinct_orgs():
    entities = {"ORG": ["Tesla", "Apple"]}
    result = validate_entities(entities)
    assert "Tesla" in result["ORG"]
    assert "Apple" in result["ORG"]


def test_validate_does_not_deduplicate_persons():
    entities = {"PERSON": ["Drake", "Drake Bell"]}
    result = validate_entities(entities)
    assert "Drake" in result["PERSON"]
    assert "Drake Bell" in result["PERSON"]


# --- validate_entities: Empty input ---

def test_validate_empty_entities():
    result = validate_entities({})
    assert result == {}


def test_validate_empty_lists():
    entities = {"PERSON": [], "ORG": []}
    result = validate_entities(entities)
    assert result == {"PERSON": [], "ORG": []}


# --- Full pipeline: extraction + validation ---

def test_duplicate_orgs_collapsed():
    text = "Apple Apple Apple in Apple Enterprise Apple HQ Apple Food Apple iPhone"
    result = extract_entities(text)
    if "ORG" in result:
        apple_count = sum(1 for name in result["ORG"] if "Apple" in name)
        assert apple_count == 1


def test_full_article():
    text = """Tesla CEO Elon Musk announced today that Tesla Inc. will expand 
    operations. Apple is expected to respond to the move, with Apple Inc. 
    reportedly developing competing technology. Goldman Sachs and Goldman 
    both issued bullish ratings."""
    result = extract_entities(text)
    assert "Elon Musk" in result.get("PERSON", [])


def test_known_orgs_in_musk_tesla_sentence():
    result = extract_entities("Elon Musk is the CEO of Tesla.")
    assert "Tesla" in result.get("ORG", [])
    assert "Apple" in result.get("ORG", [])
    assert "Apple Inc." not in result.get("ORG", [])
    assert "Tesla Inc." not in result.get("ORG", [])
