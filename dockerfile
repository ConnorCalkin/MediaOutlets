# Use stable Python version
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy project files

## RSS extraction and enrichment files
COPY extract_keywords/extractkeywords.py .
COPY rss_extraction/parsing.py .
COPY rss_extraction/scraping.py .
COPY rss_extraction/utils.py .
COPY name_entity_recognition/ner.py .
COPY sentiment_analysis/sentiment_analysis.py .
COPY store/store.py .

## Add RAG service files
COPY rag_service/rag/ingest.py .
COPY rag_service/rag/chunking.py .
COPY rag_service/rag/embedding.py .
COPY rag_service/rag/vector_store.py .

## Add pipeline file
COPY pipeline.py .

# Default command
CMD ["python", "pipeline.py"]