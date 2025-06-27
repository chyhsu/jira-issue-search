# Search Issue Service

## Description

This service provides a robust API for semantic search on Jira issues. It leverages vector embeddings to find relevant issues based on natural language queries or existing issue keys. The service includes background synchronization to keep the search index up-to-date with Jira, and all API endpoints are protected by OAuth 2.0 authentication.

## Features

*   **Semantic Search:** Find Jira issues using natural language queries.
*   **Issue Similarity:** Discover issues similar to a given Jira issue key.
*   **Jira Integration:** Fetches issues directly from a specified Jira project.
*   **Vector Embeddings:** Generates text embeddings using configurable providers (e.g., AWS Bedrock).
*   **Persistent Vector Store:** Uses ChromaDB for efficient and persistent vector search.
*   **Background Sync:** Automatically and periodically synchronizes with Jira to keep the issue index current.
*   **Secure:** All endpoints are secured using OAuth 2.0 token-based authentication.
*   **RESTful API:** Provides a clean, well-documented Flask-based API.

## Tech Stack

*   **Backend:** Python, Flask
*   **Vector Database:** ChromaDB
*   **Embedding Models:** AWS Bedrock
*   **Authentication:** OAuth 2.0 (JWT)
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
    pip install -r res/requirements.txt
    ```
4.  **Configure environment variables:**
    Create a `.env` file in the root directory and add the necessary configuration. You can copy the example file if one is provided.
    ```
    # Jira Configuration
    JIRA_URL=https://your-jira-instance.atlassian.net
    JIRA_USERNAME=your-jira-email@example.com
    JIRA_API_TOKEN=your-jira-api-token

    # ChromaDB Configuration
    CHROMA_DIR=asset/chroma_data
    COLLECTION_NAME=jira_issues

    # Embedding Provider (AWS Bedrock)
    EMBEDDING_PROVIDER=bedrock
    AWS_REGION_NAME=us-east-1
    AWS_BEDROCK_MODEL_ID=amazon.titan-embed-text-v1

    # Authentication Service
    AUTH_URL=https://your-auth-server.com
    APP_ID=your-application-id

    # Background Sync Interval
    SYNC_INTERVAL_MINUTES=60
    ```

## Running the Service

### Locally

1.  **Start the external dependencies (if needed):**
    The `Makefile` provides commands to start/stop mock external services like NATS and Ollama if required for development.
    ```bash
    make external-srv
    ```
2.  **Run the Flask application:**
    ```bash
    make run-api
    ```
    The API will be available at `http://localhost:8080`.

### With Docker

1.  **Build the Docker image:**
    ```bash
    make build-api-docker
    ```
2.  **Run the Docker container:**
    ```bash
    make run-api-docker
    ```

## Authentication

This service uses OAuth 2.0 access tokens for authentication. All API endpoints (except `/version`) require a valid `Bearer` token in the `Authorization` header. The token is validated against the configured authentication server (`AUTH_URL`).

**Example Header:**
```
Authorization: Bearer <your-jwt-token>
```

## Background Synchronization

The service includes a background scheduler that periodically synchronizes issues from Jira. The synchronization interval can be configured via the `SYNC_INTERVAL_MINUTES` environment variable. This process ensures that the search index remains up-to-date with the latest changes in the Jira project.

The synchronization logic is designed to be efficient. It only updates issues in the vector database that have been modified in Jira since their last sync time, skipping unchanged issues to save processing time and resources.

## API Endpoints

All endpoints are prefixed with `/jira`.

---

### `POST /sync`

Manually triggers the synchronization process with Jira. This is useful for forcing an immediate update outside of the regular schedule.

*   **Request Body:** None
*   **Success Response (200):**
    ```json
    {
      "code": 0,
      "message": "Sync successfully. Updated: 5, Skipped: 120",
      "updated": ["PROJ-123", "PROJ-124", "PROJ-125", "PROJ-126", "PROJ-127"]
    }
    ```

---

### `GET /query`

Performs a semantic search for issues based on a natural language query or finds issues similar to an existing issue key.

*   **Query Parameters:**
    *   `q` (string, optional): The natural language query to search for.
    *   `key` (string, optional): An existing Jira issue key to find similar issues for.
    *   `n_results` (int, optional, default: 5): The maximum number of results to return.
*   **Success Response (200):**
    ```json
    {
      "code": 0,
      "message": "Query successfully",
      "results": [
        {
          "key": "PROJ-101",
          "summary": "Button is not working on the main page",
          "distance": 0.2345
        }
      ]
    }
    ```
*   **Error Response (400):**
    ```json
    {
      "code": 400,
      "message": "Missing query parameter 'q' or 'key'"
    }
    ```

---

### `GET /suggest`

Suggests related issues based on the content of an existing Jira issue. This is a convenience endpoint that wraps the `/query` functionality for a clearer use case.

*   **Query Parameters:**
    *   `key` (string, required): The Jira issue key to get suggestions for.
*   **Success Response (200):**
    ```json
    {
      "code": 0,
      "message": "Suggest successfully",
      "results": [
        {
          "key": "PROJ-102",
          "summary": "Related issue about UI components",
          "distance": 0.3456
        }
      ]
    }
    ```
*   **Error Response (400):**
    ```json
    {
      "code": 400,
      "message": "Missing query parameter 'key'"
    }
    ```

---

### `GET /get_issues`

Retrieves a list of issues assigned to a specific user that were created after a given date.

*   **Query Parameters:**
    *   `assignee` (string, required): The assignee's email or username to filter by (e.g., `user@example.com`).
    *   `created_at` (string, required): The start date in `YYYY-MM-DDTHH:MM:SS.sss+ZZZZ` format (e.g., `2025-04-01T15:19:03.000+0800`).
    *   `n_results` (int, optional, default: 10): The maximum number of results to return.
*   **Success Response (200):**
    ```json
    {
      "code": 0,
      "message": "Get successfully",
      "results": [
        {
          "key": "PROJ-201",
          "summary": "New task assigned last week",
          "created": "2025-06-20T10:00:00.000+0800",
          "status": "In Progress"
        }
      ]
    }
    ```

---

### `GET /version`

Returns the current version of the service. This endpoint does not require authentication.

*   **Success Response (200):**
    ```json
    {
      "version": "1.0.0"
    }
    ```