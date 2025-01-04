from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from app.utils.validator import UploadValidator
from app.utils.parse_pdf import parse_pdf_file
from app.services.resume_ai import ResumeAI

app = Flask(__name__)

load_dotenv()

@app.route('/')
def index():
    return "Flask App is Running!"

@app.route('/api/pdfupload', methods=['POST'])
def upload_pdf():
    """Upload PDF and process resume"""
    # Validate request
    error, status_code = UploadValidator.validate_upload_request(request)
    if error:
        return jsonify({"error": error}), status_code
    
    # Get file and job description
    pdf_file = request.files['file']
    job_description = request.form.get('job_description', '')
    
    try:
        # Parse PDF to text
        extracted_text = parse_pdf_file(pdf_file)
        
        # Process with ResumeAI
        resume_processor = ResumeAI(extracted_text)
        result = resume_processor.process(job_description if job_description else None)
        
        return jsonify({
            "status": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Resume processing failed", 
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)