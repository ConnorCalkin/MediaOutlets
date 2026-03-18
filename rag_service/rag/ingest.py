"""
Purpose: Full pipeline for one article.
"""

from chunking import chunk_text
from embedding import get_embedding
from vector_store import add_chunks

import logging

logger = logging.getLogger(__name__)


def validate_article_text(text: str) -> None:
    """
    Validates the article text.
    """
    if not text or not text.strip():
        raise ValueError("Article text is empty")


def generate_chunks(article_id: str, text: str) -> list[str]:
    """
    Takes the full text of an article, loops through it, creating overlapping chunks.
    """
    chunks = chunk_text(text)

    if not chunks:
        logger.warning(f"No chunks created for article {article_id}")
        raise ValueError(f"No chunks created for article {article_id}")

    return chunks


def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Generates embeddings for each chunk of text.
    """
    embeddings = [get_embedding(chunk) for chunk in chunks]

    if not embeddings or any(not embedding for embedding in embeddings):
        raise RuntimeError("Failed to generate one or more embeddings")

    return embeddings


def build_metadata(article_id: str, title: str, url: str, source: str = None) -> dict:
    """
    Builds metadata dict for an article, which will be stored with each chunk.
    """
    return {
        "article_id": article_id,
        "title": title,
        "url": url,
        "source": source or ""
    }


def store_article_chunks(chunks: list[str], metadata: dict, embeddings: list[list[float]]) -> None:
    add_chunks(chunks, metadata, embeddings)


def ingest_article(article_id: str, title: str, url: str, text: str, source: str = None) -> None:
    """
    Chunks text, generate embeddings for each chunk, attach metadata, and store everything in Chroma.
    - prepares data for RAG
    """
    validate_article_text(text)
    chunks = generate_chunks(article_id, text)
    embeddings = generate_embeddings(chunks)
    metadata = build_metadata(article_id, title, url, source)
    store_article_chunks(chunks, metadata, embeddings)

    logger.info(f"Ingested article {article_id}")
