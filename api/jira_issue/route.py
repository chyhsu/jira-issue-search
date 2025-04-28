from flask import request, jsonify, Blueprint
from api.jira_issue import service
from util.logger import get_logger


jira_issue_bp = Blueprint('jira_issue', __name__)
logger = get_logger(__name__)

@jira_issue_bp.route('/sync', methods=['POST'])
def sync():
    # Call the service function to handle the sync logic
    result = service.sync_data()
    
    # Extract the updated issues and total count from the result
    updated = result.get('updated', [])
    issues_count = result.get('total', 0)
    
    logger.info(f"Sync complete. Updated: {len(updated)}, Skipped: {issues_count-len(updated)}")    
    return jsonify({'code': 0, 'message': f'Sync successfully. Updated: {len(updated)}, Skipped: {issues_count-len(updated)}', 'updated': updated})


@jira_issue_bp.route('/query', methods=['GET'])
def query():
    key = request.args.get('key')
    q = request.args.get('q')
    n_results = int(request.args.get('n_results', 5))
    logger.info(f"Querying for key: {key}, query: {q}, n_results: {n_results}")
    ret = service.query_data(key, q, n_results)
    if ret == []:
        return jsonify({'code': 0, 'message': 'No Result'})
    return jsonify({'code': 0, 'message': 'Query successfully', 'results': ret})

@jira_issue_bp.route('/suggest', methods=['GET'])
def suggest():
    key=request.args.get('key')
    logger.info(f"Suggesting for key: {key}")
    suggestion=service.suggest_data(key)
    if suggestion==[]:
        return jsonify({'code': 0, 'message': 'No Result'})
    return jsonify({'code': 0, 'message': 'Suggest successfully', 'results': suggestion})

@jira_issue_bp.route('/get_issues', methods=['GET'])
def get():
    assignee = request.args.get('assignee')
    created_after = request.args.get('created_after')
    n_results = int(request.args.get('n_results', 100))
    logger.info(f"Getting issues for assignee: {assignee}, created_after: {created_after}, n_results: {n_results}")
    results=service.get_issues(assignee, created_after, n_results)
    if results == []:
        return jsonify({'code': 0, 'message': 'No Result'})
    return jsonify({'code': 0, 'message': 'Get successfully', 'results': results})

@jira_issue_bp.route('/version', methods=['GET'])
def version():
    return jsonify({"release_version": "1.0.0.1000"})