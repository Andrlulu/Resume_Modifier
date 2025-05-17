# Empty file is sufficient
# This makes the app directory a Python package 

from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate, login_manager
import os
from dotenv import load_dotenv

def create_app(config=None):
    # Load environment variables first
    load_dotenv()

    # Create app
    app = Flask(__name__)
    
    # Configure app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://mysql:Mintmelon666!@localhost:3306/resume_app')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    db.init_app(app)
    
    # Import models to ensure they're known to Flask-Migrate
    # Models are imported automatically by importing from app.models.db
    # This ensures they are registered with Flask-SQLAlchemy
    with app.app_context():
        # Import models and explicitly register them with Flask-SQLAlchemy
        from app.models.db import User, Resume, JobDescription
        # Make sure the models are registered with db.metadata
        for model in [User, Resume, JobDescription]:
            if hasattr(model, '__table__'):
                if model.__table__.name not in db.metadata.tables:
                    db.metadata.tables[model.__table__.name] = model.__table__
    
    # Initialize Flask-Migrate after models are imported
    migrate.init_app(app, db)
    
    # Initialize login manager
    login_manager.init_app(app)
    
    # Register blueprints
    from app.server import api
    from app.web import web
    app.register_blueprint(api)
    app.register_blueprint(web)
    
    return app 