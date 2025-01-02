from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from utils.validator import UploadValidator
from utils.parse_pdf import parse_pdf_file

app = Flask(__name__)

load_dotenv()

@app.route('/')
def index():
    return "Flask App is Running!"

@app.route('/api/pdfupload', methods=['POST'])
def upload_pdf():
    """Upload PDF and return parsed text"""
    # Validate request
    error, status_code = UploadValidator.validate_upload_request(request)
    if error:
        return jsonify({"error": error}), status_code
    
    # Get file and job description
    pdf_file = request.files['file']
    job_description = request.form.get('job_description', '')
    
    try:
        # Parse PDF
        extracted_text = parse_pdf_file(pdf_file)
        return jsonify({
            "status": "success",
            "extracted_text": extracted_text,
            "text_length": len(extracted_text)
            }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Something went wrong.", 
            "details": str(e)
            }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)