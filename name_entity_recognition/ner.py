import spacy
import logging

logger = logging.getLogger("ner")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


nlp = spacy.load("en_core_web_sm")


def extract_entities(article_text):
    if not isinstance(article_text, str):
        raise TypeError("Input must be a string")

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

    logger.info("Extracted %d PERSON and %d ORG entities",
                len(entities.get("PERSON", [])),
                len(entities.get("ORG", []))
                )

    return entities


print(extract_entities(
    "Elon Musk is the CEO of Tesla. Apple Inc. is a major tech company."))
