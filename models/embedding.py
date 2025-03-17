import requests
import os

_MODEL = None
_MODEL_PATH = None

def init():
    global _MODEL
    global _MODEL_PATH
    _MODEL_PATH = os.getenv('EMBEDDING_MODEL_PATH')
    _MODEL = os.getenv('EMBEDDING_MODEL')

def get_embedding(text):

    payload = {
        "model": _MODEL,
        "prompt": text
    }
    
    # Send POST request to Ollama API
    response = requests.post(_MODEL_PATH, json=payload)
    response.raise_for_status()  # Raise an error for bad status codes
    result = response.json()
    return result['embedding']
   

def get_embedding_batch(texts):
    
    embeddings = []
    for text in texts:
        embedding = get_embedding(text)  # Reuse get_embedding for each string
        embeddings.append(embedding)
    return embeddings
    