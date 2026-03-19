FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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
RUN mkdir -p rag
COPY rag_service/rag/ingest.py rag/
COPY rag_service/rag/chunking.py rag/
COPY rag_service/rag/embedding.py rag/
COPY rag_service/rag/vector_store.py rag/

## Add pipeline file
COPY pipeline.py .

# Default command
CMD [ "pipeline.pipeline" ]
