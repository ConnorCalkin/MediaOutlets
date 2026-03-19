"""
Purpose: Expose RAG as API service.
"""

from query_functions import process_query
from flask import Flask, jsonify, request
import logging

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
    app.run(host="0.0.0.0", port=5000, debug=True)
