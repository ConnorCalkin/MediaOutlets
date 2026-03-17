"""
Purpose: Handle RAG query logic.
"""

import logging
import os

from openai import OpenAI

from rag.retrieval import retrieve_chunks

logger = logging.getLogger(__name__)


def get_retrieved_context(question: str) -> tuple[list[str], list[dict]]:
    """
    Retrieves relevant chunks and metadata for a given question.
    """
    documents, metadatas = retrieve_chunks(question)

    if not documents:
        return [], []

    logger.info(f"Retrieved {len(documents)} chunks")
    return documents, metadatas


def build_context(documents: list[str]) -> str:
    """
    Combines retrieved chunks into a single context string for the LLM.
    """
    return "\n\n".join(documents)


def generate_llm_answer(question: str, context: str) -> str:
    """
    Generates an answer from the LLM using the question and retrieved context.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Answer the question using only the provided context. If unsure, say so."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ]
    )

    return response.choices[0].message.content


def extract_sources(metadatas: list[dict]) -> list[dict]:
    """
    Extracts source information from metadata.
    """
    return [
        {
            "title": metadata.get("title"),
            "url": metadata.get("url")
        }
        for metadata in metadatas
    ]


def process_query(question: str) -> dict:
    """
    Main function to process a RAG query: retrieves context, generates answer, and extracts sources.
    """
    documents, metadatas = get_retrieved_context(question)

    if not documents:
        return {
            "answer": "No relevant information found",
            "sources": []
        }

    context = build_context(documents)
    answer = generate_llm_answer(question, context)
    sources = extract_sources(metadatas)

    return {
        "answer": answer,
        "sources": sources
    }
