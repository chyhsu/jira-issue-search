import pandas as pd
import re
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
    summary = format_value(row.get('summary', ''))
    description = format_value(row.get('description', ''))
    text = f"This is summary: '{summary}'; This is description: '{description}'"
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
    return clean_text(str(value))


