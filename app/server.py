from flask import Flask, request, jsonify
from flask_cors import CORS
from app.extensions import db, login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from app.utils.pdf_validator import PDFValidator
from app.utils.job_validator import JobValidator
from app.utils.parse_pdf import parse_pdf_file
from app.services.resume_ai import ResumeAI
from app.response_template.resume_schema import RESUME_TEMPLATE
from app.models.user import User
from app.utils.feedback_validator import FeedbackValidator
from app.utils.jwt_utils import generate_token, token_required

# Load environment variables first
load_dotenv()

# Then create app and set secret key
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://18.191.233.138:3001"])

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/resume_app')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and LoginManager
db.init_app(app)
login_manager.init_app(app)

@app.route('/')
def index():
    return "Flask App is Running!"

@app.route('/api/pdfupload', methods=['POST'])
@token_required
def upload_pdf():
    """Upload PDF and process resume"""
    # Now we can access user info from request.user
    user_id = request.user.get('user_id')
    
    # Validate request
    error, status_code = PDFValidator.validate_upload_request(request)
    if error:
        return jsonify({"error": error}), status_code
    
    # Get file
    pdf_file = request.files['file']
    
    try:
        # Parse PDF to text
        extracted_text = parse_pdf_file(pdf_file)
        
        # Process with ResumeAI - only parse
        resume_processor = ResumeAI(extracted_text)
        parsed_resume = resume_processor.parse()
        
        return jsonify({
            "status": 200,
            "data": parsed_resume
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Resume processing failed", 
            "details": str(e)
        }), 500

@app.route('/api/job_description_upload', methods=['POST'])
@token_required
def analyze_with_job():
    """Analyze resume with job description"""
    # Get user ID from token
    user_id = request.user.get('user_id')
    
    # Validate request
    error, status_code, data = JobValidator.validate_request(request)
    if error:
        return error, status_code
    
    try:
        # Process with ResumeAI
        resume_processor = ResumeAI("")  # Empty string as we're using provided resume
        resume_processor.parsed_resume = data['updated_resume']
        analysis = resume_processor.analyze(data['job_description'])

        return jsonify({
            "status": 200,
            "data": analysis
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Analysis failed",
            "details": str(e)
        }), 500

@app.route('/api/feedback', methods=['PUT'])
@token_required
def process_feedback():
    """Process feedback and updated resume data."""
    # Get user ID from token
    user_id = request.user.get('user_id')
    
    # Validate request
    error, status_code, data = FeedbackValidator.validate_request(request)
    if error:
        return error, status_code
    
    try:
        # Extract fields from validated data
        section = data['section']
        feedback = data.get('feedback', '')
        updated_resume = data['updated_resume']
        
        # Process with ResumeAI
        resume_processor = ResumeAI("")  # Empty string as we're using provided resume
        resume_processor.parsed_resume = updated_resume
        
        # Process feedback for the specific section
        analysis = resume_processor.process_section_feedback(
            section=section['section type'],
            subsection_data=section,
            feedback=feedback
        )
        
        return jsonify({
            "status": 200,
            "data": analysis
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to process feedback",
            "details": str(e)
        }), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
        
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
    
    # Create new user
    user = User(email=data['email'])
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "status": 201,
            "user": {"email": user.email}
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate input
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
        
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Generate token
    token = generate_token(user.id, user.email)
    
    return jsonify({
        "status": "success",
        "user": {"email": user.email},
        "token": token
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)