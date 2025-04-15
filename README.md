# Search Issue Service

## Description

This service provides an API to search for relevant Jira issues based on semantic similarity using vector embeddings. It fetches Jira issues, generates embeddings (using either AWS Bedrock or a local Ollama model), stores them in a ChromaDB vector database, and exposes an API endpoint for searching.

## Features

*   Fetches issues from Jira.
*   Generates text embeddings using configurable providers (AWS Bedrock, Ollama).
*   Stores embeddings in ChromaDB for persistent vector search.
*   Provides a Flask-based API for searching issues.
*   Centralized logging.
*   Dockerized for easier deployment.

## Tech Stack

*   **Backend:** Python, Flask
*   **Vector Database:** ChromaDB
*   **Embedding Models:** AWS Bedrock / Ollama
*   **Containerization:** Docker

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd search-issue-service
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure environment variables:**
    Copy the `.env.example` file to `.env` and fill in the required values (Jira credentials, ChromaDB path, Embedding provider settings, AWS credentials if using Bedrock).
    ```bash
    cp .env.example .env
    # Edit .env with your details
    ```

## Configuration

Environment variables are managed using a `.env` file. Key variables include:

*   `FLASK_ENV`: Application environment (e.g., `development`, `production`)
*   `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`: Jira connection details.
*   `CHROMA_DIR`: Path to the ChromaDB persistent storage directory (default: `asset/chroma_data`).
*   `COLLECTION_NAME`: ChromaDB collection name (default: `jira_issues`).
*   `EMBEDDING_PROVIDER`: `bedrock` or `ollama`.
*   `OLLAMA_MODEL`, `OLLAMA_BASE_URL`: Ollama configuration (if used).
*   `AWS_REGION_NAME`, `AWS_BEDROCK_MODEL_ID`: AWS Bedrock configuration (if used).
*   *Add any other relevant variables.*

## Usage

1.  **Generate Embeddings (if needed):**
    *(Add command or script name here if you have one, e.g., `python scripts/generate_embeddings.py`)*

2.  **Run the API server:**
    ```bash
    flask run
    ```
    Or using Docker:
    ```bash
    docker build -t search-issue-service -f res/docker/api.Dockerfile .
    docker run -p 5000:5000 --env-file .env search-issue-service
    ```

3.  **API Endpoints:**

    *   `POST/sync`: Trigger synchronization with Jira.
        *   **Request Body:** None
        *   **Response:** `{"code": 0, "message": "Sync successfully. Updated: X, Skipped: Y", "updated": ["KEY-1", ...]}`

    *   `GET/query`: Search for relevant issues.
        *   **Query Parameters:**
            *   `q` (string, optional): The natural language query to search for.
            *   `key` (string, optional): An existing Jira issue key to find similar issues.
            *   `n_results` (int, optional, default: 5): The maximum number of results to return.
        *   **Response:** `{"code": 0, "message": "Query successfully", "results": [...]}` or `{"code": 0, "message": "No Result"}`

    *   `GET/suggest`: Suggest related issues based on an existing issue.
        *   **Query Parameters:**
            *   `key` (string, required): The Jira issue key to get suggestions for.
        *   **Response:** `{"code": 0, "message": "Suggest successfully", "results": [...]}` or `{"code": 0, "message": "No Result"}`

   

