"""
Purpose: Find relevant chunks for a question.
"""

from rag.embedding import get_embedding
from rag.vector_store import collection

import logging

logger = logging.getLogger(__name__)


def retrieve_chunks(query: str, k: int = 3):
    """
    Embed the question, query Chroma, return top K matching chunks and their metadata.
    - selects useful content for the LLM
    """
    try:
        # 1. Embed query
        query_embedding = get_embedding(query)

        # 2. Query Chroma
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        logger.info(f"Retrieved {len(documents)} chunks")

        return documents, metadatas

    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return [], []
