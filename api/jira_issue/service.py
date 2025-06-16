import os
from db.chroma import insert_or_replace_batch,insert_or_replace_one, get_one_by_key,query,get
from util.txt_process import  format_value, document
from api.jira_issue.jira_source import fetch_by_query, fetch_by_id
from models.embedding import get_embedding_bedrock
from models.suggest import  get_suggestion_bedrock
from util.logger import get_logger
import concurrent.futures
from util.txt_process import format_time_to_txt, format_time_to_iso
import time 
from threading import Thread 
from datetime import datetime, timedelta 

logger = get_logger(__name__)


_sync_thread = None
_keep_sync_running = True 
SYNC_INTERVAL_SECONDS = 3600 


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

    logger.info("Starting Jira data sync...")
    issues = fetch_by_query(jira_query,fetch_size)
    # result_to_df(issues)
    
    # Issues that need to be updated
    to_update = []
    updated = []
    
    # First pass: identify all issues that need updating
    logger.info("Identifying issues that need updating...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(100, fetch_size)) as executor:
        futures = [executor.submit(check_if_needed_update, issue) for issue in issues]
        for future in concurrent.futures.as_completed(futures):
            issue = future.result()
            if issue:
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
            # document([issue]) returns a list with one string, get that string for Bedrock
            query_text = document([issue])[0] 
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
            'assignee': metadata.get('assignee','None'),
            'issuetype': metadata.get('issuetype','None'),
            'description': metadata.get('description','None'),
            'comment':metadata.get('comment'),
            'status': metadata.get('status'),
            'created': format_time_to_txt(metadata.get('created', 'No created date available'))
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
    ret['suggestion']=get_suggestion_bedrock(existed_issue['document'])
    return ret


def get_issues(assignee, created_after=None, n_results=10):
    ret=[]
    created_after_iso = format_time_to_iso(created_after)
    metadata_filters = {
        "$and": [
            {"assignee": {"$eq": assignee}},
            {"created": {"$gte": created_after_iso}}
        ]
    }
    results = get(**metadata_filters)
    for doc in results['metadatas']:
        ret.append({
            'key': doc['key'],
            'summary': doc.get('summary', 'No summary available'),
            'url': doc.get('url', 'No URL available'),
            'assignee': doc.get('assignee','None'),
            'issuetype': doc.get('issuetype','None'),
            'description': doc.get('description','None'),
            'status': doc.get('status'),
            'created': format_time_to_txt(doc.get('created', 'No created date available'))
        })
    return ret


def _sync_scheduler_loop():
    """Internal loop for the sync scheduler thread."""
    global _keep_sync_running
    logger.info("Sync scheduler thread started.")
    while _keep_sync_running:
        try:
            logger.info(f"Scheduler: Calling sync_data at {datetime.now()}")
            sync_data()
            logger.info(f"Scheduler: sync_data finished. Next sync in {SYNC_INTERVAL_SECONDS} seconds.")
        except Exception as e:
            logger.error(f"Error during scheduled sync_data: {e}", exc_info=True)
        
        # Wait for the interval, but check _keep_sync_running periodically
        # to allow for faster shutdown if needed.
        for _ in range(SYNC_INTERVAL_SECONDS):
            if not _keep_sync_running:
                break
            time.sleep(1)
            
    logger.info("Sync scheduler thread stopped.")

def start_background_sync():
    """Starts the background sync scheduler thread if not already running."""
    global _sync_thread
    if _sync_thread is None or not _sync_thread.is_alive():
        _sync_thread = Thread(target=_sync_scheduler_loop, daemon=True)
        _sync_thread.start()
        logger.info("Background sync thread initiated.")
    else:
        logger.info("Background sync thread is already running.")

def stop_background_sync():
    """Signals the background sync scheduler thread to stop."""
    global _keep_sync_running
    _keep_sync_running = False
    if _sync_thread and _sync_thread.is_alive():
        logger.info("Attempting to stop background sync thread...")
        _sync_thread.join(timeout=10) # Wait for the thread to finish
        if _sync_thread.is_alive():
            logger.warning("Background sync thread did not stop in time.")
    else:
        logger.info("Background sync thread was not running or already stopped.")


def check_if_needed_update(issue):

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

        # Check if created date changed
        if isinstance(metadata.get('created'),str):
            logger.info(f"Created date changed for {issue['key']}")
            need_update = True
        elif metadata.get('created') != format_time_to_iso(issue.get('created')):
            logger.info(f"Created date changed for {issue['key']}")
            need_update = True
        
        # Check if assignee changed
        if metadata.get('assignee') != issue.get('assignee'):
            logger.info(f"Assignee changed for {issue['key']}: {metadata.get('assignee')} -> {issue.get('assignee')}")
            need_update = True
        
        # Check if comments added or deleted
        if metadata.get('comment_num') != issue.get('comment_num'):
            logger.info(f"The number of comments changed for {issue['key']}")
            need_update = True

        if need_update:
            # Add to batch for update
            return issue
    else:
        # Issue doesn't exist, add to batch
        logger.info(f"Issue {issue['key']} doesn't exist")
        return issue
