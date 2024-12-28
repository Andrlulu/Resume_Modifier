from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.utils.parse_pdf import parse_pdf_file
from app.utils.openai_utils import analyze_text_with_openai

api_bp = Blueprint('api', __name__)

@api_bp.route('/pdfupload/', methods=['POST'])
def upload_pdf():
    # Check Authorization Header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization is missing."}), 403

    # Check Content-Type
    if 'multipart/form-data' not in request.content_type:
        return jsonify({"error": "Content-Type must be multipart/form-data"}), 400

    # Check if 'file' is in the request
    if 'file' not in request.files:
        return jsonify({"error": "Please provide PDF."}), 400

    pdf_file = request.files['file']
    job_description = request.form.get('job_description', '')

    if pdf_file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Uploaded file must be a PDF."}), 400

    try:
        # Secure the filename
        filename = secure_filename(pdf_file.filename)
        # Optionally, save the file if needed
        # pdf_file.save(os.path.join('/path/to/save', filename))

        # Parse PDF
        extracted_text = parse_pdf_file(pdf_file)

        # Analyze with OpenAI
        analysis = analyze_text_with_openai(extracted_text, job_description)

        return jsonify({"status": 200, "data": analysis}), 200

    except Exception as e:
        return jsonify({"error": "Something went wrong.", "details": str(e)}), 500
