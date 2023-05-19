import datetime
import os

from pymongo import MongoClient

_CLIENT = None
_DB = None
_COLL = None

def init():
    global _CLIENT, _DB, _COLL
    _CLIENT = MongoClient(host=os.getenv('MONGO_HOST'),
                          username=os.getenv('MONGO_AUTH_USERNAME'),
                          password=os.getenv('MONGO_AUTH_PASSWORD'),
                          authSource=os.getenv('MONGO_AUTH_DATABASE'),
                          authMechanism='SCRAM-SHA-1',
                          connect=False)
    if _CLIENT is None:
        print('failed to connect to Mongo')
        return
    _DB = _CLIENT[os.getenv('MONGO_DBNAME')]
    _COLL = _DB["security_jira_issue"]


def get_all():
    return list(_COLL.find())


def get_one_by_key(key):
    return _COLL.find_one({'_id': key})


def insert_or_replace_one(key, status, summary, description, document, embedding):
    now = datetime.datetime.utcnow()
    _COLL.update_one(
        {'_id': key},
        {
            '$set': {
                'status': status,
                'summary': summary,
                'description': description,
                'document': document,
                'embedding': embedding,
                'updated_at': now
            },
            '$setOnInsert': {
                'created_at': now
            }
        },
        upsert=True
    )


def update_one(key, status, summary, description, document, embedding):
    now = datetime.datetime.utcnow()
    _COLL.update_one(
        {'_id': key},
        {
            '$set': {
                'status': status,
                'summary': summary,
                'description': description,
                'document': document,
                'embedding': embedding,
                'updated_at': now
            }
        }
    )
