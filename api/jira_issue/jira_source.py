import os
import pandas as pd
from jira import JIRA
import urllib3
from util.logger import get_logger
from util.txt_process import format_time_to_iso
# Get a logger for this module
logger = get_logger(__name__)

def fetch_by_query(query, num_of_issues_to_fetch=1000):
    JIRA_URL = os.getenv('JIRA_URL')
    JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
    if not [JIRA_URL, JIRA_API_TOKEN]:
        logger.error("JIRA_URL or JIRA_API_TOKEN not found in environment variables")
        return None

    # Initialize JIRA client
    jira_options = {'server': JIRA_URL, 'verify': False}  
    # This will suppress InsecureRequestWarning that comes from using verify=False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    JIRA_CLIENT = JIRA(options=jira_options, token_auth=JIRA_API_TOKEN)

    # Initialization
    ret = []
    start_at = 0
    max_results = min(1000, num_of_issues_to_fetch)   # maximal result per api call is 1000
    total = None
    
    # Continue fetching until we've got all results
    while total is None or start_at < total:

        # Fetch a batch of issues
        issues = JIRA_CLIENT.search_issues(
            query, 
            startAt=start_at, 
            maxResults=max_results, 
            fields='key,summary,status,description,created,issuetype,assignee,comment'
        )
        
        # If this is the first batch, get the total number of results
        if total is None:  
            total = min(num_of_issues_to_fetch, issues.total)
    
        # Process the current batch
        for issue in issues:
            issue_dict = create_issue_structure(issue)
            if issue_dict:
                ret.append(issue_dict)
        
        # If we got fewer results than requested, we're done
        if len(issues) < max_results:
            break
        
        # Move to the next batch
        start_at += len(issues)
        logger.info(f"Fetching {start_at} issues")
        # Adjust max_results for the last batch
        if total-start_at<max_results:
            max_results=total-start_at
        
    return ret


def fetch_by_id(jira_id):

    JIRA_URL = os.getenv('JIRA_URL')
    JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
    
    jira_options = {'server': JIRA_URL, 'verify': False}
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    JIRA_CLIENT = JIRA(options=jira_options, token_auth=JIRA_API_TOKEN)
    
    # Fetch the issue
    issue = JIRA_CLIENT.issue(jira_id, fields='key,summary,status,description,created,issuetype,assignee,comment')
            
    return create_issue_structure(issue)


def result_to_df(result):
    CSV_PATH = os.getenv('CSV_PATH')    
    if result:
        df = pd.DataFrame.from_dict(result)
        df.to_csv(CSV_PATH, index=False, header=True)

def create_issue_structure(issue):
    
    # print(issue.fields.comment.comments[0].author.name) 
    # Get assignee information if available
    assignee_name = 'Unassigned'
    if hasattr(issue.fields, 'assignee') and issue.fields.assignee:
        assignee_name = issue.fields.assignee.name
    
    comment=""
    for c in issue.fields.comment.comments:
        comment += f'{c.author.name}: {c.body}, '
    
    created_at_iso = format_time_to_iso(issue.fields.created)
    issue_url = f"https://qnap-jira.qnap.com.tw/browse/{issue.key}"
    return {
        'key': issue.key,
        'status': issue.fields.status.name,
        'summary': issue.fields.summary,
        'description': issue.fields.description,
        'created': created_at_iso,
        'comment': comment,
        'comment_num':issue.fields.comment.total,
        'issuetype': issue.fields.issuetype.name,
        'assignee': assignee_name,
        'url': issue_url
    }
