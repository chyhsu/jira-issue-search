import os
import logging
import pandas as pd

import database
import jira_source
import text_embedding
import similarity

from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set the desired logging level


@app.route('/sync', methods=['POST'])
def sync_data():
    issues = jira_source.fetch_by_query(os.getenv('JIRA_QUERY'))
    for issue in issues:
        need_update = False
        app.logger.debug('processing issue: %s', issue['key'])
        existed_issue = database.get_one_by_key(issue['key'])
        if existed_issue:
            if existed_issue["status"] != issue["status"]:
                need_update = True
                existed_issue["status"] = issue["status"]
            if existed_issue["summary"] != issue["summary"] or existed_issue["description"] != issue["description"]:
                need_update = True
                existed_issue.update(issue)
                existed_issue['document'] = text_embedding.document(existed_issue['summary'], existed_issue['description'])
                existed_issue['embedding'] = text_embedding.get_embedding(existed_issue['document'])
        else:
            need_update = True
            existed_issue = {}
            existed_issue.update(issue)
            existed_issue['document'] = text_embedding.document(issue['summary'], issue['description'])
            existed_issue['embedding'] = text_embedding.get_embedding(existed_issue['document'])
        if need_update:
            database.insert_or_replace_one(
                existed_issue["key"],
                existed_issue["status"],
                existed_issue["summary"],
                existed_issue["description"],
                existed_issue["document"],
                existed_issue["embedding"])
    return jsonify({'code': 0, 'message': 'Sync successfully'})


@app.route('/query', methods=['GET'])
def query():
    key = request.args.get('key')
    q = request.args.get('q')

    # get embedding
    if key:
        # check if issue already exists
        existed_issue = database.get_one_by_key(key)
        if not existed_issue:
            issue = jira_source.fetch_by_id(key)
            existed_issue = {}
            existed_issue.update(issue)
            existed_issue['document'] = text_embedding.document(issue['summary'], issue['description'])
            existed_issue['embedding'] = text_embedding.get_embedding(existed_issue['document'])
            database.insert_or_replace_one(
                existed_issue["key"],
                existed_issue["status"],
                existed_issue["summary"],
                existed_issue["description"],
                existed_issue["document"],
                existed_issue["embedding"])
        prompt_embedding = existed_issue['embedding']
    else:
        prompt_embedding = text_embedding.get_embedding(q)

    # get all existing issues
    df = pd.DataFrame(database.get_all())

    # calculate similarity
    df['similarity'] = df['embedding'].apply(
        lambda vector: similarity.vector_similarity(vector, prompt_embedding)
    )
    ret = []
    for _, row in df.nlargest(11, 'similarity').iterrows():
        if key and row['_id'] == key: continue
        ret.append({
            'key': row['_id'],
            'summary': row['summary'],
            'description': row['description'],
            'similarity': row['similarity']
        })

    return jsonify(ret)


if __name__ == '__main__':
    database.init()
    app.run(host='0.0.0.0', port=8080)
