from flask import Flask
from dotenv import load_dotenv
import logging
import os
from util.logger import setup_logging, logger

def create_app():
    app = Flask(__name__)
    
    # Configure centralized logging
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    setup_logging(getattr(logging, log_level.upper(), logging.INFO))
    
    # Initialize services
    init_services()
    
    # Register blueprints
    from app.jira_issue.route import jira_issue_bp
    app.register_blueprint(jira_issue_bp)
   
    logger.info("Application initialized successfully")
    return app

def init_services():

    # Load environment variables
    load_dotenv()

    # Initialize ChromaDB using our db module
    import db.chroma
    db.chroma.init()
    
    # Initialize embedding model
    import models.embedding
    models.embedding.init()
    
    # Log successful initialization
    logger.info("All services initialized successfully")
