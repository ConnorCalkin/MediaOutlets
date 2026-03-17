import spacy
from typing import List

# Load spaCy model once (avoids reloading on every function call)
nlp = spacy.load("en_core_web_sm")

# Curated high-impact media terms for celebrity PR analysis
IMPACT_TERMS = {
    "scandal", "controversy", "backlash", "cancelled", "lawsuit", "arrest",
    "relationship", "dating", "breakup", "divorce", "engagement", "wedding",
    "affair", "cheating", "married", "rumors", "viral", "headline",
    "exclusive", "marriage", "award", "nomination", "premiere",
    "red carpet", "brand deal", "collaboration"
}


def validate_input_text(text) -> List[str]:
    """
    Validates the input text before keyword extraction is attempted.

    Two cases are handled explicitly:
        - Non-string input: raises a TypeError with a descriptive message,
          since passing the wrong type to spaCy would produce a confusing
          internal error rather than a clear one.
        - Empty string: returns an empty list immediately, as there is
          nothing to extract from a blank input.

    Args:
        text: The raw input to validate. Intentionally untyped so the
              function can catch and report non-string values.

    Returns:
        List[str]: An empty list if text is an empty string.

    Raises:
        TypeError: If text is not a string (e.g. None, int, list).
    """
    if not isinstance(text, str):
        raise TypeError(
            f"Input must be a string, got {type(text).__name__} instead."
        )
    if text == "":
        return []
    return None


def extract_location_and_event_entities(doc: spacy.tokens.Doc) -> List[str]:
    """
    Extracts named entities representing locations, dates, and events from a spaCy Doc.

    Targets entity labels:
        - GPE (Geopolitical Entity): countries, cities, states
        - LOC (Location): non-GPE locations, e.g. mountain ranges
        - DATE: absolute or relative dates and periods
        - EVENT: named events, e.g. awards shows, festivals

    Explicitly excludes PERSON entities to avoid capturing celebrity names.

    Args:
        doc (spacy.tokens.Doc): A processed spaCy document.

    Returns:
        List[str]: Lowercased entity texts matching the target labels.
    """
    target_labels = {"GPE", "LOC", "DATE", "EVENT"}
    return [
        entity.text.lower()
        for entity in doc.ents
        if entity.label_ in target_labels
    ]


def extract_impact_tokens(doc: spacy.tokens.Doc) -> List[str]:
    """
    Extracts individual adjective and noun tokens that appear in the IMPACT_TERMS dictionary.

    Filters out:
        - Stop words (e.g. "the", "is")
        - Punctuation
        - Tokens shorter than 3 characters
        - Any part-of-speech other than ADJ (adjective) or NOUN

    This catches standalone high-signal words like "scandal" or "viral" that
    may not appear inside a noun chunk.

    Args:
        doc (spacy.tokens.Doc): A processed spaCy document.

    Returns:
        List[str]: Lowercased token texts that are impactful adjectives or nouns.
    """
    return [
        token.text.lower()
        for token in doc
        if not token.is_stop
        and not token.is_punct
        and len(token.text) >= 3
        and token.pos_ in {"ADJ", "NOUN"}
        and token.text.lower() in IMPACT_TERMS
    ]


def deduplicate_preserving_order(keywords: List[str]) -> List[str]:
    """
    Removes duplicate keywords while preserving their original insertion order.

    Uses a dict (ordered in Python 3.7+) rather than a set to maintain the
    order in which keywords were first encountered — important for ranking
    relevance by position in the source text.

    Args:
        keywords (List[str]): A list of keywords that may contain duplicates.

    Returns:
        List[str]: The same keywords with duplicates removed, order preserved.
    """
    return list(dict.fromkeys(keywords))


def extract_keywords_spacy(text) -> List[str]:
    """
    Extracts high-value keywords from text using spaCy for celebrity PR/media analysis.

    Begins by validating the input via validate_input_text, then orchestrates
    three extraction strategies on the parsed document:
        1. Named entities — locations, dates, and events
        2. Noun chunks    — multi-word phrases containing high-impact PR terms
        3. Token scan     — individual impactful adjectives and nouns

    Duplicates are removed while preserving the order keywords first appear.
    PERSON entities (celebrity names) are intentionally excluded throughout.

    Args:
        text: Input article or text to analyze. Must be a non-empty string.

    Returns:
        List[str]: Unique, cleaned keywords relevant to PR insights.
        Returns an empty list if text is an empty string.

    Raises:
        TypeError: If text is not a string.
    """
    validation_result = validate_input_text(text)
    if validation_result is not None:
        return validation_result

    doc = nlp(text)

    keywords = (
        extract_location_and_event_entities(doc)
        + extract_impact_tokens(doc)
    )

    return deduplicate_preserving_order(keywords)


if __name__ == "__main__":
    sample_text = """
    Sarah Jane is in a new relationship with actor Tom Smith. They were spotted
    on a romantic date in Paris last weekend. This comes after Sarah's recent
    breakup with her ex-husband, which was surrounded by scandal.
    The new couple were seen together at the Grammys, sparking rumors of an exclusive romance.
    """

    # Test normal usage
    extracted_keywords = extract_keywords_spacy(sample_text)
    print("Extracted Keywords:", extracted_keywords)
