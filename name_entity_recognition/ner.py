import spacy

nlp = spacy.load("en_core_web_sm")


def extract_entities(article_text: str) -> dict:
    """
    Extracts named entities from the given article text and categorizes them by type (PERSON, ORG).
    """
    doc = nlp(article_text)

    entities = {}
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG"):
            if ent.label_ not in entities:
                entities[ent.label_] = set()
            entities[ent.label_].add(ent.text)

    return {key: list(values) for key, values in entities.items()}


print(extract_entities("Apple Inc. was founded by Steve Jobs and Steve Wozniak."))
