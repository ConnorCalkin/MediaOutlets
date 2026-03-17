import chromadb
from chromadb.utils import embedding_functions

import logging

logger = logging.getLogger(__name__)

# Create client (local)
client = chromadb.Client()

# Create/get collection
collection = client.get_or_create_collection(name="articles")


def add_chunks(chunks: list[str], metadata: dict, embeddings: list[list[float]]):
    """
    Store chunks with embeddings in Chroma
    """
    try:
        ids = [f"{metadata['article_id']}_{i}" for i in range(len(chunks))]

        metadatas = [
            {
                **metadata,
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(
            f"Stored {len(chunks)} chunks for article {metadata['article_id']}")

    except Exception as e:
        logger.error(f"Failed to store chunks: {e}")
