import requests
import os
from tqdm import tqdm
import json
import boto3
import concurrent.futures
from util.logger import get_logger

_MODEL = None
_MODEL_PATH = None

BEDROCK_REGION = None
BEDROCK_ACCESS_KEY_ID = None
BEDROCK_SECRET_ACCESS_KEY = None
BEDROCK_EMBEDDING_MODEL_ID = None

logger = get_logger(__name__)

def init():
    global _MODEL
    global _MODEL_PATH
    _MODEL_PATH = os.getenv('EMBEDDING_MODEL_PATH')
    _MODEL = os.getenv('EMBEDDING_MODEL')

    global BEDROCK_REGION
    global BEDROCK_ACCESS_KEY_ID
    global BEDROCK_SECRET_ACCESS_KEY
    global BEDROCK_EMBEDDING_MODEL_ID
    BEDROCK_REGION = os.getenv('BEDROCK_REGION')
    BEDROCK_ACCESS_KEY_ID = os.getenv('BEDROCK_ACCESS_KEY_ID')
    BEDROCK_SECRET_ACCESS_KEY = os.getenv('BEDROCK_SECRET_ACCESS_KEY')
    BEDROCK_EMBEDDING_MODEL_ID = os.getenv('BEDROCK_EMBEDDING_MODEL_ID')


def get_embedding(text):

    payload = {
        "model": _MODEL,
        "prompt": text
    }
    response = requests.post(_MODEL_PATH, json=payload)
    response.raise_for_status() 
    result = response.json()
    return result['embedding']
   

def get_embedding_batch(texts):
    
    embeddings = []
    for text in tqdm(texts, desc="Generating embeddings", unit="text"):
        embedding = get_embedding(text)  
        embeddings.append(embedding)
    return embeddings

def get_embedding_bedrock(text):

    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=BEDROCK_REGION,
        aws_access_key_id=BEDROCK_ACCESS_KEY_ID,
        aws_secret_access_key=BEDROCK_SECRET_ACCESS_KEY,
    )

    payload = {
        "inputText": text
    }
    
    response = bedrock_runtime.invoke_model(
        body=json.dumps(payload),
        modelId=BEDROCK_EMBEDDING_MODEL_ID,
        accept="application/json",
        contentType="application/json"
    )
    response_body = json.loads(response.get('body').read())
    return response_body['embeddingsByType']['float']

def get_embedding_bedrock_batch(texts):
    size = len(texts)
    batch_size = 50
    num_batches = (size + batch_size - 1) // batch_size
    embeddings = []
    
    for i in tqdm(range(num_batches), desc="Generating embeddings", unit="batch"):
        batch_start = i * batch_size
        batch_end = min(batch_start + batch_size, size)
        batch = texts[batch_start:batch_end]

        batch_embeddings = [None] * len(batch) 
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(50, len(batch))) as executor:
            future_to_index = {executor.submit(get_embedding_bedrock, text): idx 
                              for idx, text in enumerate(batch)}
            
            for future in concurrent.futures.as_completed(future_to_index):
                idx = future_to_index[future]
                batch_embeddings[idx] = future.result()
        
        embeddings.extend(batch_embeddings)
    
    return embeddings