from flask import request, jsonify, Blueprint
from app.jira_issue import service
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
    return jsonify({'code': 0, 'message': 'Query successfully', 'results': ret})


@jira_issue_bp.route('/version', methods=['GET'])
def version():
    return jsonify({"release_version": "1.0.0.1000"})