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


def extract_keywords_spacy(text: str) -> List[str]:
    """
    Extracts high-value keywords from a text using spaCy.

    This function is designed for celebrity PR/media analysis and focuses on:
    - Locations, dates, and events (via Named Entity Recognition)
    - Relationship and trending phrases (via noun chunk extraction)
    - High-impact PR terms (via custom dictionary matching)

    It explicitly excludes PERSON entities (e.g., celebrity names).

    Args:
        text (str): Input article or text to analyze.

    Returns:
        List[str]: A list of unique, cleaned keywords relevant to PR insights.
    """

    if not text:
        return []

    doc = nlp(text)
    extracted_keywords = []

    # Capture locations (GPE/LOC), dates, and events
    for entity in doc.ents:
        if entity.label_ in {"GPE", "LOC", "DATE", "EVENT"}:
            extracted_keywords.append(entity.text.lower())

    # Capture meaningful phrases like "secret relationship"
    for noun_chunk in doc.noun_chunks:
        chunk_text = noun_chunk.text.lower().strip()

        if any(term in chunk_text for term in IMPACT_TERMS):
            extracted_keywords.append(chunk_text)

    # Capture individual impactful words (adjectives + nouns)
    for token in doc:
        if token.is_stop or token.is_punct or len(token.text) < 3:
            continue

        if token.pos_ in {"ADJ", "NOUN"}:
            token_text = token.text.lower()

            if token_text in IMPACT_TERMS:
                extracted_keywords.append(token_text)

    unique_keywords = list(dict.fromkeys(extracted_keywords))

    return unique_keywords


if __name__ == "__main__":
    sample_text = """
    Sarah Jane is in a new relationship with actor Tom Smith. They were spotted
    on a romantic date in Paris last weekend. This comes after Sarah's recent
    breakup with her ex-husband, which was surrounded by scandal.
    The new couple were seen together at the Grammys, sparking rumors of an exclusive romance.
    """

    extracted_keywords = extract_keywords_spacy(sample_text)
    print("Extracted Keywords:", extracted_keywords)
