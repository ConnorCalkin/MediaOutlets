"""
Purpose: Store chunks in Chroma.
"""

import os
import chromadb

import logging

logger = logging.getLogger(__name__)

<<<<<<< feature/pipeline
# Create client (local)
# TODO: update to connect to remote Chroma instance when deployed
client = chromadb.Client()
=======

def get_chroma_client():
    chroma_host = os.getenv("CHROMA_HOST", "localhost")
    chroma_port = os.getenv("CHROMA_PORT", "8000")

    return chromadb.HttpClient(
        host=chroma_host,
        port=chroma_port
    )


# Create client
client = get_chroma_client()
>>>>>>> main

# Create/get collection
collection = client.get_or_create_collection(name="articles")


def add_chunks(chunks: list[str], metadata: dict, embeddings: list[list[float]]):
    """
    Saves chunk text, embedding, and metadata.
    - allows for fast semantic search later
    """
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
