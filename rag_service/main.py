"""
Purpose: Simple entry point to test RAG ingestion into Chroma.
"""

from ingest import ingest_article


def main():
    title = "Test Article"
    url = "https://example.com/test-article"
    text = """
    OpenAI released new tooling for developers building retrieval-augmented generation systems.
    These systems often use chunking, embeddings, and a vector database to retrieve relevant context.
    Chroma can store embeddings and metadata for semantic search.
    AWS services such as Lambda, API Gateway, ECS, and EFS can be used to deploy a RAG architecture.
    """

    ingest_article(
        title=title,
        url=url,
        text=text,
    )

    print("Article ingested successfully.")


if __name__ == "__main__":
    main()
