from flask import Request

class JobValidator:
    @staticmethod
    def validate_request(request: Request):
        """Validate job description request"""
        if not request.get_data(as_text=True):
            return ("Job description is required", 400)
        
        return (None, None) 