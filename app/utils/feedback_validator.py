from flask import Request, jsonify

class FeedbackValidator:
    @staticmethod
    def validate_request(request: Request):
        """Validate feedback request"""
        # Validate content type
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        # Get and validate JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400
            
        # Validate required fields
        section = data.get('section')
        if not section:
            return jsonify({"error": "Section is required"}), 400
            
        if 'section type' not in section:
            return jsonify({"error": "Section type is required"}), 400
            
        updated_resume = data.get('updated_resume')
        if not updated_resume:
            return jsonify({"error": "Updated resume is required"}), 400
            
        return None, None, data 