from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from app.utils.pdf_validator import PDFValidator
from app.utils.job_validator import JobValidator
from app.utils.parse_pdf import parse_pdf_file
from app.services.resume_ai import ResumeAI

# Load environment variables first
load_dotenv()

# Then create app and set secret key
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    return "Flask App is Running!"

@app.route('/api/pdfupload', methods=['POST'])
def upload_pdf():
    """Upload PDF and process resume"""
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
        
        # Store in session and print for debugging
        session['extracted_text'] = extracted_text
        session['parsed_resume'] = parsed_resume
        print("Session after PDF upload:", dict(session))
        
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
def analyze_with_job():
    """Analyze resume with job description"""
    print("Current session:", dict(session))
    
    # Validate request
    error, status_code = JobValidator.validate_request(request)
    if error:
        return jsonify({"error": error}), status_code
    
    try:
        # Get job description from request body
        job_description = request.get_data(as_text=True)
        
        # Check if we have the parsed resume
        if 'parsed_resume' not in session or 'extracted_text' not in session:
            return jsonify({
                "error": "Please upload a resume first"
            }), 400
            
        # Create ResumeAI instance with stored text and parsed resume
        resume_processor = ResumeAI(session['extracted_text'])
        resume_processor.parsed_resume = session['parsed_resume']
        
        # Only do analysis
        analysis = resume_processor.analyze(job_description)
        
        return jsonify({
            "status": 200,
            "data": analysis
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Analysis failed",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)