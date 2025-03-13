from sentence_transformers import SentenceTransformer
import os

_MODEL = None

def init():
    global _MODEL
    _MODEL = os.getenv('MODEL')


def get_embedding(text):
    # Load embedding model
    model = SentenceTransformer(_MODEL, trust_remote_code=True) 
    # Get embedding function
    embedding = model.encode(text, show_progress_bar=True).tolist()
    return embedding

def get_embedding_batch(texts):
    model = SentenceTransformer(_MODEL, trust_remote_code=True)
    # Get embeddings for all texts in batch    
    embeddings = model.encode(texts, show_progress_bar=True).tolist()
    return embeddings