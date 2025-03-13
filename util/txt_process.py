import pandas as pd
import re
from models.embedding import get_embedding_batch
from util.logger import get_logger

# Get a logger for this module
logger = get_logger(__name__)

def clean_text(text):
    if not text or pd.isna(text):
        return ""
    # Remove special characters and formatting
    text = str(text)
    text = re.sub(r'\[.*?\]', '', text)  # Remove content in square brackets
    text = re.sub(r'<.*?>', '', text)    # Remove HTML tags
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
    
    return text.strip()

def document(row):

    # Clean and prepare the text
    summary = clean_text(row.get('summary', ''))
    description = clean_text(row.get('description', ''))
    text = f"{summary} {description}"
    return text


def format_value(value, default=''):
  
    if value is None:
        return default
    if isinstance(value, str):
        # Convert whitespace-only strings to empty strings
        if value.strip() == '':
            return ''
        return value
    if isinstance(value, (int, float, bool)):
        return value
    return str(value)


def create_entry(issues):
  
    # Create document text
    doc_texts = []
    for issue in issues:
        doc_text = document(issue)
        doc_texts.append(doc_text)
    
    # Generate embeddings in batch (much more efficient)
    embeddings = get_embedding_batch(doc_texts)

    # Create URLs with consistent format
    issue_urls = []
    for issue in issues:
        issue_key = issue.get('key')
        issue_url = f"https://qnap-jira.qnap.com.tw/browse/{issue_key}"
        issue_urls.append(issue_url)
    
    # Create metadata with consistent format
    metadatas = []
    for i, issue in enumerate(issues):
        metadata = {
            'key': issue.get('key'),
            'status': issue.get('status'),
            'created': issue.get('created'),
            'summary': format_value(issue.get('summary')),
            'description': format_value(issue.get('description')),
            'issuetype': issue.get('issuetype'),
            'assignee': issue.get('assignee'),
            'url': issue_urls[i]
        }
        metadatas.append(metadata)
    
    return doc_texts, embeddings, metadatas