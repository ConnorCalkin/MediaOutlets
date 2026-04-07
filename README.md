# Media Pulse: Automated Media Intelligence

**Media Pulse** is an end-to-end automated media monitoring and analysis platform. It transforms raw RSS feeds from major global news outlets into actionable insights using Natural Language Processing (NLP) and a Retrieval-Augmented Generation (RAG) architecture. 

Designed for talent managers and PR professionals, Media Pulse provides a cost-effective, scalable solution for tracking sentiment, entities, and coverage trends in real-time.

---

## Features

* **Automated Data Pipeline**: Scrapes articles from RSS feeds (e.g., BBC Entertainment, Business) every 6 hours using `newspaper4k`.
* **NLP Enrichment**: 
    * **Named Entity Recognition (NER)**: Powered by `spaCy` to track people, organizations, and locations.
    * **Sentiment Analysis**: Powered by `VADER` to monitor public perception.
* **Interactive Dashboard**: A Streamlit interface providing real-time article feeds, sentiment trend visualizations, and entity frequency charts.
* **RAG-Powered Query Server**: A natural language interface that allows users to query the scraped database (e.g., "What is the recent sentiment regarding Company X?") using ChromaDB and LLM integration.
* **Cloud Native Architecture**: Built on AWS for high availability, utilizing serverless components to minimize maintenance.

---

## Architecture

The system is built on a modern AWS stack to ensure scalability and cost-efficiency:

-   **Orchestration**: AWS EventBridge triggers periodic Lambda executions.
-   **Compute**: AWS Lambda (Pipeline & RAG processing) and ECS Fargate (Dashboard & Vector Database).
-   **Storage**: 
    -   **Amazon S3**: Raw article content.
    -   **Amazon DynamoDB**: Article metadata and entity metrics.
    -   **Amazon EFS**: Persistent storage for the ChromaDB vector index.
-   **Vector Search**: ChromaDB running on ECS Fargate.
-   
---

## ⚙️ Getting Started

The following steps will allow you to deploy the architecture on your AWS account

### Prerequisites
* **Python 3.10+**
* **AWS CLI** configured with appropriate permissions.
* **Docker** (Required for local ChromaDB and Dashboard testing).
* **OpenAI API Key** (For the RAG Query Server).

### AWS Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/ConnorCalkin/MediaOutlets.git
   cd MediaOutlets
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
3. **Configure Environment:**
   Add the following to a .tfvars file in the `terraform` directory
   ```
   openai_api_key = "your-api-key"
   chroma_host = "your-chroma-host"
   chroma_port = "your-chroma-port"
   ```
4. **Initialise Terraform:**
   ```
   cd terraform
   terraform init
   terraform apply
   ```
5. **Initialise RAG Terraform:**
   ```
   cd rag_infra
   terraform init
   terraform apply
   ```


## Future Steps

- [ ] **Expanded Data Sources**: Integration with social media APIs and broadcast transcripts.
- [ ] **Transformer-based NLP**: Upgrade to `en_core_web_trf` for higher NER accuracy.
- [ ] **Automated Reporting**: Daily/Weekly PDF newsletters sent to subscribers via SES.
- [ ] **Real-Time Alerts**: Push notifications for sudden negative sentiment spikes.
- [ ] **Multi-Language Support**: Extending the pipeline to support non-English news sources.

---

## 👥 The Team: Dashboard Divas (Otranto Development)

* **Zaria Farooq-Khan** – Project Manager
* **Pragya Sinha** – Architect & DevOps
* **Connor Calkin** – Data & Business Analyst
* **Edmond Doda** – QA Tester
