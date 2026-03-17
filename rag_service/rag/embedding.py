"""
Purpose: Convert text into vectors.
"""

import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)


def get_embedding(text: str) -> list[float]:
    """
    Sends the text to OpenAI, which returns the embedding.
    - enables similarity search in vector DB
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )

        embedding = response.data[0].embedding

        logger.info("Embedding created successfully")

        return embedding

    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return []
