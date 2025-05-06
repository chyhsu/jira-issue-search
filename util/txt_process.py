import pandas as pd
import re
from util.logger import get_logger
import concurrent.futures
from datetime import datetime, timezone, timedelta
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(100, rows_size)) as executor:
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

def format_time_to_iso(time_str):
    if not isinstance(time_str, str):
        return time_str
    else:
        if time_str[-5] == " ":
            time_str = time_str[:-5] + "+" + time_str[-4:]
        dt = datetime.fromisoformat(time_str)
        return int(dt.astimezone(timezone.utc).timestamp())

def format_time_to_txt(time):
    if not isinstance(time, (int, float)):
        return str(time)  # Return the string as is if it's not a numeric timestamp
    return datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    