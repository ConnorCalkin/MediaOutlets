"""
This module will chunk the article body, ready for embedding.
"""

import logging

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 500) -> list[str]:
    """
    Split text into overlapping character-based chunks.
    """
    if not text or not text.strip():
        logger.warning("Received empty or invalid text for chunking")
        return []

    chunks = []
    start = 0
    text = text.strip()

    try:
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            start += chunk_size - overlap

        logger.info(f"Created {len(chunks)} chunks")

        return chunks

    except Exception as e:
        logger.error(f"Chunking failed: {e}")
        return []
