# Search Issue Service

A Flask-based service for searching and retrieving Jira issues using semantic search with embeddings.

## Overview

This service provides a REST API for:
- Syncing Jira issues to a local ChromaDB database
- Querying similar issues based on semantic search
- Retrieving issue details

The application uses sentence transformers to generate embeddings for Jira issue content, enabling powerful semantic search capabilities beyond simple keyword matching.

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
│   └── embedding.py        # Embedding model functions
├── util/                   # Utility modules
│   ├── __init__.py
│   ├── logger.py           # Centralized logging
│   └── txt_process.py      # Text processing utilities
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
└── run.py                  # Application entry point
```

## Setup and Installation

### Prerequisites

- Python 3.9+
- Access to a Jira instance
- Sufficient disk space for storing embeddings

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
   export JIRA_USER="your-jira-username"
   export JIRA_PASSWORD="your-jira-password"
   export JIRA_QUERY='PROJECT = "YOUR-PROJECT"'
   export JIRA_URL="your-jira-url"
   export JIRA_API_TOKEN="your-jira-api-token"
   export CSV_PATH="asset/jira.csv"
   export CHROMA_DIR="asset/chroma_data"
   export COLLECTION_NAME="jira_issues"
   export MODEL="sentence-transformers/all-MiniLM-L12-v2"
   export FETCH_SIZE=5000
   ```

5. Create the asset directory:
   ```
   mkdir -p asset/chroma_data
   ```

## Running the Application

Start the application with:

```
python run.py
```

The service will be available at `http://0.0.0.0:8080`.

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
[
  {
    "key": "PROJ-124",
    "summary": "Login page not working in Safari",
    "distance": 0.123
  },
  ...
]
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

## Deployment

The service can be deployed using Docker and Kubernetes. See the deployment documentation for details.

## License

[Specify your license here]
