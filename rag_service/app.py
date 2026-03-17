"""
This module defines the Flask application that serves as the API for the RAG system.
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
logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route("/query", methods=["POST"])
def query():
    try:
        data = request.get_json()
        question = data.get("question")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        # 1. Retrieve relevant chunks
        documents, metadatas = retrieve_chunks(question)

        if not documents:
            return jsonify({"answer": "No relevant information found", "sources": []})

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

        return jsonify({
            "answer": answer,
            "sources": sources
        })

    except Exception as e:
        logging.error(f"Query failed: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
