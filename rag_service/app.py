"""
Purpose: Expose RAG as API service.
"""


from flask import Flask, request, jsonify

from rag.retrieval import retrieve_chunks
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

from rag.ingest import ingest_article

load_dotenv()

app = Flask(__name__)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route("/query", methods=["POST"])
def query():
    """
    Receives a question (query), calls retrieval, builds context, sends to OpenAI LLM, and returns
    answer and sources.
    - make system usable by users
    """
    try:
        data = request.get_json()
        question = data.get("question")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        logger.info(f"Received query: {question}")

        # 1. Retrieve relevant chunks
        documents, metadatas = retrieve_chunks(question)

        if not documents:
            return jsonify({"answer": "No relevant information found", "sources": []})

        logger.info(f"Retrieved {len(documents)} chunks")

        # 2. Build context
        context = "\n\n".join(documents)

        # 3. Call LLM
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

        answer = response.choices[0].message.content

        # 4. Extract sources
        sources = []
        for meta in metadatas:
            sources.append({
                "title": meta.get("title"),
                "url": meta.get("url")
            })

        logger.info("Successfully generated response")

        return jsonify({
            "answer": answer,
            "sources": sources
        })

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
