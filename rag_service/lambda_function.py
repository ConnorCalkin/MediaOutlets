"""
Purpose: Expose RAG as Lambda API service.
"""

import json
import logging

from dotenv import load_dotenv
from query_functions import process_query

load_dotenv()

logger = logging.getLogger(__name__)


def get_question_from_event(event: dict) -> str:
    """
    Extracts the question from the Lambda event body.
    """
    body = event.get("body")

    if not body:
        raise ValueError("No JSON body provided")

    data = json.loads(body)

    question = data.get("question")

    if not question:
        raise ValueError("No question provided")

    return question


def lambda_handler(event, context):
    """
    Main Lambda handler for RAG queries.
    Expects event body with "question" field.
    Returns answer and sources.
    """
    try:
        question = get_question_from_event(event)
        logger.info(f"Received query: {question}")

        result = process_query(question)

        logger.info("Successfully generated response")
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except ValueError as e:
        logger.error(f"Bad request: {e}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
