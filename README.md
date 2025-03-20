# Search Issue Service

A Flask-based service for searching and retrieving Jira issues using semantic search with embeddings.

## Overview

This service provides a REST API for:
- Syncing Jira issues to a local ChromaDB database
- Querying similar issues based on semantic search
- Retrieving issue details
- Getting AI-powered suggestions for issue solutions

The application uses embeddings to generate vector representations of Jira issue content, enabling powerful semantic search capabilities beyond simple keyword matching. It also integrates with Ollama to provide AI-powered suggestions for issue resolution.

## Project Structure

```
search-issue-service/
├── app/                    # Main application package
│   ├── __init__.py         # Application factory and initialization
│   └── jira_issue/         # Jira issue module
│       ├── __init__.py
│       ├── jira_source.py  # Functions for fetching data from Jira
│       ├── route.py        # API route handlers
│       └── service.py      # Business logic for syncing and querying
├── db/                     # Database interaction modules
│   ├── __init__.py
│   └── chroma.py           # ChromaDB interface
├── models/                 # ML models and embedding functions
│   ├── __init__.py
│   ├── embedding.py        # Embedding model functions
│   └── suggest.py          # AI suggestion generation using Ollama
├── util/                   # Utility modules
│   ├── __init__.py
│   ├── logger.py           # Centralized logging
│   └── txt_process.py      # Text processing utilities
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
├── Makefile                # Commands for running and managing the service
└── run.py                  # Application entry point
```

## Setup and Installation

### Prerequisites

- Python 3.9+
- Access to a Jira instance
- Sufficient disk space for storing embeddings
- Ollama server running locally or accessible via port-forwarding

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd search-issue-service
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   # Jira Configuration
   JIRA_QUERY='PROJECT = "YOUR-PROJECT" OR ASSIGNEE= "user1@example.com" OR ASSIGNEE= "user2@example.com"'
   JIRA_URL="your-jira-url"
   JIRA_API_TOKEN="your-basic-auth-token"
   FETCH_SIZE=2000

   # ChromaDB Configuration
   CSV_PATH="asset/jira.csv"
   CHROMA_DIR="asset/chroma_data"
   COLLECTION_NAME="jira_issues"

   # Ollama Configuration (for local embedding and suggestion generation)
   EMBEDDING_MODEL_PATH="http://localhost:11434/api/embeddings"
   EMBEDDING_MODEL="mxbai-embed-large"
   SUGGEST_MODEL_PATH="http://localhost:11434/api/chat"
   SUGGEST_MODEL="gemma3"

   # AWS Bedrock Configuration (alternative to local Ollama)
   BEDROCK_REGION="your-aws-region"
   BEDROCK_ACCESS_KEY_ID="your-aws-access-key-id"
   BEDROCK_SECRET_ACCESS_KEY="your-aws-secret-access-key"
   BEDROCK_EMBEDDING_MODEL_ID="amazon.titan-embed-text-v2:0"
   BEDROCK_SUGGEST_MODEL_ID="us.deepseek.r1-v1:0"
   ```

   > **Note:** You can choose to use either local Ollama or AWS Bedrock for generating embeddings and suggestions. If you configure both, the application will prioritize AWS Bedrock by default.

5. Create the asset directory:
   ```
   mkdir -p asset/chroma_data
   ```

6. Start required external services:
   ```
   make external-srv
   ```

## Running the Application

Start the application with:

```
python run.py
```

The service will be available at `http://0.0.0.0:8080`.

Alternatively, you can run the service in Docker:

```
make run-api-docker
```

## API Endpoints

### Sync Jira Issues

```
POST /sync
```

Fetches issues from Jira based on the configured query and stores them in the local ChromaDB database.

**Response:**
```json
{
  "code": 0,
  "message": "Sync successfully. Updated: 10, Skipped: 90",
  "updated": ["PROJ-123", "PROJ-124", ...]
}
```

### Query Similar Issues

```
GET /query?key=PROJ-123&n_results=5
```

or

```
GET /query?q=How to fix the login issue&n_results=5
```

Searches for issues similar to the specified issue key or query text.

**Parameters:**
- `key` (optional): Jira issue key to find similar issues
- `q` (optional): Text query to find relevant issues
- `n_results` (optional, default=5): Number of results to return

**Response:**
```json
{
  "code": 0,
  "message": "Query successfully",
  "results": [
    {
      "key": "PROJ-124",
      "summary": "Login page not working in Safari",
      "url": "https://jira.example.com/browse/PROJ-124",
      "distance": 0.123,
      "text": "Full text of the issue"
    },
    ...
  ]
}
```

### Get AI Suggestions for an Issue

```
GET /suggest?key=PROJ-123
```

Retrieves AI-generated suggestions for resolving a specific issue.

**Parameters:**
- `key`: Jira issue key to get suggestions for

**Response:**
```json
{
  "code": 0,
  "message": "Suggest successfully",
  "results": {
    "summary": "Issue summary",
    "description": "Issue description",
    "suggestion": "AI-generated suggestion for resolving the issue"
  }
}
```

### Get All Issues

```
GET /get?n_results=10
```

Retrieves a list of all issues in the database.

**Parameters:**
- `n_results` (optional, default=5): Number of results to return

**Response:**
```json
{
  "code": 0,
  "message": "Get successfully",
  "results": [
    {
      "key": "PROJ-123",
      "summary": "Issue summary",
      ...
    },
    ...
  ]
}
```

### Version Information

```
GET /version
```

Returns the current version of the service.

**Response:**
```json
{
  "release_version": "1.0.0.1000"
}
```

## Configuration Options

### Embedding Generation Options

The service supports two methods for generating embeddings:

1. **Local Ollama** - Uses a locally running Ollama server with models like `mxbai-embed-large`
2. **AWS Bedrock** - Uses Amazon's Bedrock service with models like `amazon.titan-embed-text-v2:0`

To configure which method to use:
- For local Ollama: Set the `EMBEDDING_MODEL_PATH` and `EMBEDDING_MODEL` variables in `.env`
- For AWS Bedrock: Set the `BEDROCK_*` variables in `.env`

The application will automatically use AWS Bedrock if properly configured, otherwise it will fall back to the local Ollama model.

### Suggestion Generation Options

Similarly, AI suggestions can be generated using:

1. **Local Ollama** - Uses models like `gemma3` running on your local Ollama server
2. **AWS Bedrock** - Uses models like `us.deepseek.r1-v1:0` or other available Bedrock models

To configure which method to use:
- For local Ollama: Set the `SUGGEST_MODEL_PATH` and `SUGGEST_MODEL` variables in `.env`
- For AWS Bedrock: Set the `BEDROCK_SUGGEST_MODEL_ID` and other `BEDROCK_*` variables in `.env`

## Development

### Adding New Features

1. Create appropriate module files in the relevant package
2. Update the application factory in `app/__init__.py` if adding new blueprints
3. Add tests for new functionality

### Logging

The application uses a centralized logging system. To add logging to a new module:

```python
from util.logger import get_logger
logger = get_logger(__name__)

# Then use it
logger.info("Starting process")
logger.debug("Detailed information")
```

### External Services

The application relies on the following external services:

1. **Jira API** - For fetching issue data
2. **Ollama** - For generating embeddings and AI suggestions
3. **NATS Server** - For message queue functionality

You can start these services using:
```
make external-srv
```

And stop them using:
```
make clean-external-srv
```

## Deployment

The service can be deployed using Docker and Kubernetes. A sample Kubernetes deployment for Ollama is provided in the repository.

## License

[Specify your license here]
