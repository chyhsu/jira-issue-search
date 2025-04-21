import pandas as pd
import re
from util.logger import get_logger
import concurrent.futures
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

def document(rows):

    rows_size = len(rows)

    def process_row(row):
        key = format_value(row.get('key', ''))
        summary = format_value(row.get('summary', ''))
        description = format_value(row.get('description', ''))
        return f"This is Issue ID: '{key}'; This is summary: '{summary}'; This is description: '{description}'"

    if rows_size == 1:
        row = rows[0]
        return [process_row(row)]

    result = [None] * rows_size
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, rows_size)) as executor:
        future_to_index = {
            executor.submit(process_row, rows[i]): i 
            for i in range(rows_size)
        }
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            result[index] = future.result()
    return result


def format_value(value, default=''):
  
    if value is None:
        return default
    if isinstance(value, str):
        if value.strip() == '':
            return ''
        return value
    if isinstance(value, (int, float, bool)):
        return value
    return clean_text(str(value))
