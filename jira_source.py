import os
import pandas as pd
from jira import JIRA

JIRA_CLIENT = JIRA(
    os.getenv('JIRA_URL'),
    token_auth=os.getenv('JIRA_TOKEN'))


def fetch_by_query(query):
    ret = []
    issues = JIRA_CLIENT.search_issues(
        query, startAt=0, maxResults=1000, fields='key,summary,status,description')
    for issue in issues:
        ret.append({
            'key': issue.key,
            'status': issue.fields.status.name,
            'summary': issue.fields.summary,
            'description': issue.fields.description
        })
    return ret


def fetch_by_id(jira_id):
    issue = JIRA_CLIENT.issue(jira_id)
    return {
            'key': issue.key,
            'status': issue.fields.status.name,
            'summary': issue.fields.summary,
            'description': issue.fields.description
    }


if __name__ == '__main__':
    result = fetch_by_query(os.getenv('JIRA_QUERY'))
    df = pd.DataFrame.from_dict(result)
    df.to_csv('jira.csv', index=False, header=True)
