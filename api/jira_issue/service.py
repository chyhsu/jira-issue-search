import os
from db.chroma import insert_or_replace_batch,get_all,insert_or_replace_one, get_one_by_key,query
from util.txt_process import  format_value, document
from api.jira_issue.jira_source import result_to_df, fetch_by_query, fetch_by_id
from models.embedding import get_embedding_bedrock
from models.suggest import  get_suggestion_bedrock
from util.logger import get_logger

logger = get_logger(__name__)

def sync_data():
    """
    Sync data from Jira to the local Chroma database.
    
    Returns:
        dict: A dictionary containing the sync results with keys:
            - updated: list of updated issue keys
            - total: total number of issues processed
    """
    jira_query=os.getenv('JIRA_QUERY')
    fetch_size=int(os.getenv('FETCH_SIZE'))

    issues = fetch_by_query(jira_query,fetch_size)
    result_to_df(issues)
    
    # Issues that need to be updated
    to_update = []
    updated = []
    
    # First pass: identify all issues that need updating
    logger.info("Identifying issues that need updating...")
    for issue in issues:
        need_update = False
        # Get existing issue from database
        existed_issue = get_one_by_key(issue['key'])
        
        if existed_issue:
            metadata = existed_issue['metadata']
            
            # Direct comparisons - the format should be consistent now
            if metadata.get('status') != issue.get('status'):
                logger.info(f"Status changed for {issue['key']}: {metadata.get('status')} -> {issue.get('status')}")
                need_update = True
            
            # Check if summary or description changed
            if metadata.get('summary') != issue.get('summary'):
                logger.info(f"Summary changed for {issue['key']}")
                need_update = True
                
            # Special handling for description - normalize empty values        
            if format_value(metadata.get('description')) != format_value(issue.get('description')):
                logger.info(f"Description changed for {issue['key']}")
                need_update = True

            if need_update:
                # Add to batch for update
                to_update.append(issue)
                updated.append(issue.get('key'))
        else:
            # Issue doesn't exist, add to batch
            logger.info(f"Issue {issue['key']} doesn't exist")
            to_update.append(issue)
            updated.append(issue.get('key'))
    
    # Second pass: process all updates at once
    if to_update:
        logger.info(f"Processing {len(to_update)} issues")
        insert_or_replace_batch(to_update)
    
    # Return the results
    return {
        'updated': updated,
        'total': len(issues)
    }

def query_data(key,q,n_results):
    """
    Query the Jira database for issues based on a key or a query string.

    Args:
        key (str, optional): The unique key of a Jira issue.
        q (str, optional): The query string to search for in the Jira database.
        n_results (int): The number of results to return.

    Returns:
        list: A list of dictionaries containing the query results.
    """
    ret = []
    if key:
        # Check if issue already exists
        existed_issue = get_one_by_key(key)
        if not existed_issue:
            logger.info("Issue doesn't exist")
            # If not, fetch it and add to database
            try:
                issue = fetch_by_id(key)
            except Exception as e:
                logger.error(f"Failed to fetch issue {key}: {e}")
                return []
            insert_or_replace_one(issue)
            query_text = document(issue)
            query_embedding = get_embedding_bedrock(query_text)
        else:
            query_embedding = existed_issue['embedding']
    else:
        # Use the provided query text
        query_text = format_value(q)
        query_embedding = get_embedding_bedrock(query_text)

    # Use ChromaDB's built-in query functionality
    results = query(query_embedding, n_results)
    
    # Process results
    for i in range(len(results['ids'][0])):
        result_key = results['ids'][0][i]
        # Get metadata for this result
        metadata = results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'] else {}
        
        # Add to results
        ret.append({
            'key': result_key,
            'summary': metadata.get('summary', 'No summary available'),
            'url': metadata.get('url', 'No URL available'),
            'distance': float(results['distances'][0][i]) if 'distances' in results else 0.0,
            'created': metadata.get('created', 'No created date available')
        })
      
        # If we have enough results after filtering, break
        if len(ret) >= n_results:
            break  
    return ret
    
def suggest_data(key):
    ret={}
    existed_issue = get_one_by_key(key)
    if not existed_issue:
        return []
    ret['summary']=existed_issue['metadata']['summary']
    ret['description']=existed_issue['metadata']['description']
    ret['suggestion']=get_suggestion_bedrock(existed_issue['document'])
    return ret


def get_data(n_results):
    ret=[]
    results = get_all()
    for doc in results['metadatas']:
        text=f"This is summary: '{doc['summary']}'; This is description: '{doc['description']}'"
        ret.append({
            'text': text,
            'key': doc['key'],
            'suggestion':""
        })
    return ret[:n_results]