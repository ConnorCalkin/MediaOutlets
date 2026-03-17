"""
This module defines the full ingestion pipeline for an article, including 
chunking the text, generating embeddings, and storing the chunks and metadata 
in ChromaDB. 
"""

from rag.chunking import chunk_text
from rag.embedding import get_embedding
from rag.vector_store import add_chunks

import logging

logger = logging.getLogger(__name__)


def ingest_article(article_id: str, title: str, url: str, text: str, source: str = None):
    """
    Full ingestion pipeline for one article
    """
    try:
        # 1. Chunk
        chunks = chunk_text(text)

        if not chunks:
            logger.warning(f"No chunks created for article {article_id}")
            return

        # 2. Embed
        embeddings = [get_embedding(chunk) for chunk in chunks]

        # 3. Metadata
        metadata = {
            "article_id": article_id,
            "title": title,
            "url": url,
            "source": source or ""
        }

        # 4. Store in Chroma
        add_chunks(chunks, metadata, embeddings)

        logger.info(f"Ingested article {article_id}")

    except Exception as e:
        logger.error(f"Ingestion failed for article {article_id}: {e}")
