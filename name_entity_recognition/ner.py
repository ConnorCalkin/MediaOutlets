import spacy
import logging

logger = logging.getLogger("ner")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

nlp = spacy.load("en_core_web_sm")


def validate_entities(entities):
    """
    Cleans up extracted entities by:
    1. Removing entities longer than 4 words
    2. Removing single character entities
    3. Removing PERSON entities that aren't capitalised
    4. Removing ORG entities that contain other ORG entities within them (keeping the shorter version)
    """
    validated = {}

    for label, names in entities.items():
        # Filter by length
        filtered = [name for name in names if 1 < len(
            name.strip()) and len(name.split()) <= 4]

        # PERSON entities must be capitalised
        if label == "PERSON":
            filtered = [name for name in filtered if all(
                word[0].isupper() for word in name.split())]

        # Remove ORG entities that contain other ORG entities (keep the shortest)
        if label == "ORG":
            sorted_names = sorted(filtered, key=len)
            unique = []
            for name in sorted_names:
                if not any(existing.lower() in name.lower() and existing != name for existing in unique):
                    unique.append(name)
            filtered = unique

        validated[label] = filtered

    return validated


def extract_entities(article_text):
    """
    Extracts PERSON and ORG entities from the given article text,
    returning a dictionary with entity types as keys and lists of unique entity names as values.
    """
    if not isinstance(article_text, str):
        raise TypeError("Input must be a string")

    article_text = article_text.strip()
    if not article_text:
        return {}

    logger.info("Starting entity extraction for text of length %d",
                len(article_text))

    doc = nlp(article_text)

    entities = {}
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG"):
            if ent.label_ not in entities:
                entities[ent.label_] = set()
            entities[ent.label_].add(ent.text)

    entities = {key: list(values) for key, values in entities.items()}
    entities = validate_entities(entities)

    logger.info("Extracted %d PERSON and %d ORG entities",
                len(entities.get("PERSON", [])),
                len(entities.get("ORG", []))
                )

    return entities

print(extract_entities(
    "Elon Musk is the CEO of Tesla. Apple Inc. is a major tech company."))
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print(
        extract_entities(
            """Tesla CEO Elon Musk announced today that Tesla Inc. will expand 
            operations into Jordan, following a meeting with Jordan's King Abdullah II. 
            Musk, who also leads SpaceX, confirmed that the Tesla factory in Berlin 
            will begin producing a new model by March 2026. Apple is expected to respond 
            to the move, with Apple Inc. reportedly developing competing technology. 
            Industry analyst Michael Jordan commented that this could reshape the entire 
            EV market. Goldman Sachs and Goldman both issued bullish ratings."""
        )
    )
