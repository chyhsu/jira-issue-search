from flask import Flask
from dotenv import load_dotenv
import logging
import os
from util.logger import setup_logging, logger
from util.token import create_token_service
from flask import request, jsonify

def create_app():
    app = Flask(__name__)
    auth_url = os.environ.get('AUTH_URL')
    app_id = os.environ.get('APP_ID')
    token_service = create_token_service(auth_url, app_id)
    
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    setup_logging(getattr(logging, log_level.upper(), logging.INFO))
    
    # Add access token check middleware
    @app.before_request
    def check_token():
        if request.path == '/version':
            return None
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            return jsonify({'code': 401, 'message': 'Access token is missing'}), 401
        token_info = token_service.get_token_info(token)
        if isinstance(token_info, str):
            return jsonify({'code': 401, 'message': token_info}), 401
        if not token_info.to_dict().get('user').get('id'):
            return jsonify({'code': 401, 'message': 'Invalid access token'}), 401
    # Initialize services
    init_services()
    
    # Register blueprints
    from api.jira_issue.route import jira_issue_bp
    app.register_blueprint(jira_issue_bp)
   
    logger.info("Application initialized successfully")
    return app

def init_services():

    # Load environment variables
    load_dotenv()

    # Initialize ChromaDB using our db module
    import db.chroma
    db.chroma.init()

    import models.suggest
    models.suggest.init()


    # Initialize embedding model
    import models.embedding
    models.embedding.init()
    
    # Log successful initialization
    logger.info("All services initialized successfully")
