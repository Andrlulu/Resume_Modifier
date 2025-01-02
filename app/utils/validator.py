from flask import Request

class UploadValidator:
    @staticmethod
    def validate_upload_request(request: Request):
        """Validate PDF upload request"""
        if 'multipart/form-data' not in request.content_type:
            return ("Content-Type must be multipart/form-data", 400)
        
        # Check if file exists
        if 'file' not in request.files:
            return ("No file uploaded", 400)
                
        # Check filename
        if request.files['file'].filename == '':
            return ("No file selected for uploading", 400)       
        
        # Check file type
        if not request.files['file'].filename.lower().endswith('.pdf'):
            return ("Uploaded file must be a PDF.", 400)
        
        return (None, None)