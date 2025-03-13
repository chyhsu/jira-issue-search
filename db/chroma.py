import chromadb
import os
from util.txt_process import create_entry

CLIENT = None
COLLECTION = None

def init():
    global CLIENT
    global COLLECTION

    # Load constants from environment variables

    CHROMA_DIR = os.getenv('CHROMA_DIR')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME')

    # Initialize Chroma CLIENT and get COLLECTION
    CLIENT = chromadb.PersistentClient(path=CHROMA_DIR)
    COLLECTION = CLIENT.get_or_create_collection(name=COLLECTION_NAME)

def get_one_by_key(key):
    # Query the COLLECTION for the exact key
    results = COLLECTION.get(
        ids=[key],
        include=["metadatas", "documents", "embeddings"]
    )
    
    # Check if we found any results
    if results and 'ids' in results and len(results['ids']) > 0:
        # Create a structured response similar to MongoDB
        return {
            '_id': results['ids'][0],
            'document': results['documents'][0] if 'documents' in results and len(results['documents']) > 0 else None,
            'embedding': results['embeddings'][0] if 'embeddings' in results and len(results['embeddings']) > 0 else None,
            'metadata': results['metadatas'][0] if 'metadatas' in results and len(results['metadatas']) > 0 else {}
        }
    return None

def get_all():
    return COLLECTION.get()


def insert_or_replace_one(issue):
   
    key = issue.get('key', '')
    document, embedding, metadata = create_entry([issue])

    # Use upsert to handle both insert and update cases in a single operation
    COLLECTION.upsert(
        ids=[key],
        documents=[document],
        embeddings=[embedding],
        metadatas=[metadata]
    )


def insert_or_replace_batch(issues):
   
    # Extract keys for IDs
    ids = [issue.get('key', '') for issue in issues if issue.get('key', '')]

    # Use the enhanced create_entry function to process all issues at once
    documents, embeddings, metadatas = create_entry(issues)
    
    # Use upsert to handle both insert and update cases in a single operation
    COLLECTION.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
def query(query_text, n_results=5):
   
    # Use ChromaDB's built-in query functionality
    results = COLLECTION.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results

    