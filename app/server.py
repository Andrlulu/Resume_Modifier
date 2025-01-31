from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import jwt
from dotenv import load_dotenv
from app.utils.pdf_validator import PDFValidator
from app.utils.job_validator import JobValidator
from app.utils.parse_pdf import parse_pdf_file
from app.services.resume_ai import ResumeAI
from app.response_template.resume_schema import RESUME_TEMPLATE
import time

# Load environment variables first
load_dotenv()

# Then create app and set secret key
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://18.191.233.138:3001"])
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')

def create_token(data: dict) -> str:
    """Create JWT token with resume data"""
    return jwt.encode(data, JWT_SECRET, algorithm='HS256')

@app.route('/')
def index():
    return "Flask App is Running!"

@app.route('/api/pdfupload', methods=['POST'])
def upload_pdf():
    """Upload PDF and process resume"""
    print("\n=== PDF Upload Started ===")
    start_time = time.time()
    
    # Validate request
    error, status_code = PDFValidator.validate_upload_request(request)
    if error:
        return jsonify({"error": error}), status_code
    
    # Get file
    pdf_file = request.files['file']
    
    try:
        # Parse PDF to text
        print("Starting PDF parsing...")
        parse_start = time.time()
        extracted_text = parse_pdf_file(pdf_file)
        print(f"PDF parsing took: {time.time() - parse_start:.2f} seconds")
        
        # Process with ResumeAI - only parse
        print("Starting AI processing...")
        ai_start = time.time()
        resume_processor = ResumeAI(extracted_text)
        parsed_resume = resume_processor.parse()
        print(f"AI processing took: {time.time() - ai_start:.2f} seconds")
        
        # Time token generation
        print("Starting token generation...")
        token_start = time.time()
        token = create_token({
            'extracted_text': extracted_text,
            'parsed_resume': parsed_resume
        })
        print(f"Token generation took: {time.time() - token_start:.2f} seconds")
        
        print(f"Total request took: {time.time() - start_time:.2f} seconds")
        print("=== PDF Upload Completed ===\n")
        
        return jsonify({
            "status": 200,
            "data": parsed_resume,
            "token": token
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Resume processing failed", 
            "details": str(e)
        }), 500

@app.route('/api/job_description_upload', methods=['POST'])
def analyze_with_job():
    """Analyze resume with job description"""
    print("\n=== Job Analysis Started ===")
    start_time = time.time()
    
    # Validate request
    error, status_code = JobValidator.validate_request(request)
    if error:
        return jsonify({"error": error}), status_code
    
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "No token provided"}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        # Decode token
        token_data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        extracted_text = token_data['extracted_text']
        parsed_resume = token_data['parsed_resume']
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
    try:
        # Get job description from request body
        job_description = request.get_data(as_text=True)
        
        # Process with ResumeAI
        print("Starting AI analysis...")
        ai_start = time.time()
        resume_processor = ResumeAI(extracted_text)
        resume_processor.parsed_resume = parsed_resume
        analysis = resume_processor.analyze(job_description)
        print(f"AI analysis took: {time.time() - ai_start:.2f} seconds")
        
        print(f"Total request took: {time.time() - start_time:.2f} seconds")
        print("=== Job Analysis Completed ===\n")
        
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
def process_feedback():
    """Process feedback and updated resume data."""
    try:
        # Validate content type
        if request.content_type != 'application/json':
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 400

        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "No token provided"}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        try:
            # Decode token
            token_data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            extracted_text = token_data['extracted_text']
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        # Get JSON data directly from request
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Missing request body"
            }), 400

        # Extract fields from data
        section = data.get('section')
        feedback = data.get('feedback', '')
        updated_resume = data.get('updated_resume')

        # Validate required fields
        if not section:
            return jsonify({
                "error": "Section is required"
            }), 400

        if not updated_resume:
            return jsonify({
                "error": "Updated resume is required"
            }), 400

        # Create ResumeAI instance with data from token
        resume_processor = ResumeAI(extracted_text)
        resume_processor.parsed_resume = updated_resume

        # Process feedback for the specific section
        analysis = resume_processor.process_section_feedback(
            section=section.get('section type'),
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)