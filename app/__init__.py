from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables at startup
load_dotenv()

# Add debug print (remove in production!)
print(f"Loaded API key: {os.getenv('OPENAI_API_KEY')[:6]}...")

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Basic configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

    # Register blueprints with URL prefix '/api'
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Add a simple root route to confirm the app is running
    @app.route('/')
    def home():
        return "Flask App is Running!"

    return app
