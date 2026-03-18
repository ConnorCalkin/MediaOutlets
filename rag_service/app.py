"""
Purpose: Expose RAG as API service.
"""

from query_functions import process_query
from flask import Flask, jsonify, request
import logging
from rag.ingest import ingest_article

from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
logger = logging.getLogger(__name__)


def get_question_from_request() -> str:
    """
    Extracts the question from the incoming JSON request.
    """
    data = request.get_json()

    if not data:
        raise ValueError("No JSON body provided")

    question = data.get("question")

    if not question:
        raise ValueError("No question provided")

    return question


@app.route("/query", methods=["POST"])
def query():
    """
    Main API endpoint for RAG queries. Expects JSON body with "question" field. 
    Returns answer and sources.
    """
    try:
        question = get_question_from_request()
        logger.info(f"Received query: {question}")

        result = process_query(question)

        logger.info("Successfully generated response")
        return jsonify(result)

    except ValueError as e:
        logger.error(f"Bad request: {e}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    ingest_article(
        article_id="test-1",
        title="Angela Rayner's explosive speech reignites leadership speculation",
        url="https://www.bbc.co.uk/news/articles/cpd8d10n9x5o",
        text="Angela Rayner's fiery speech at the Labour conference has reignited speculation about her future in the party leadership. The Labour Party's deputy leader delivered a passionate address, criticizing the government's handling of key issues and calling for unity within the party. Her remarks have been interpreted by some as a challenge to current leader Keir Starmer, leading to renewed discussions about potential leadership changes within Labour.",
    )
    app.run(debug=True)
