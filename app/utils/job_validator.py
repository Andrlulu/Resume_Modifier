from flask import Request

class JobValidator:
    @staticmethod
    def validate_request(request):
        """Validate job description upload request"""
        # Check if there's content
        if not request.data:
            return "No job description provided", 400
            
        # Check content length (optional)
        content = request.get_data(as_text=True)
        if len(content) < 10:  # Minimum length
            return "Job description too short", 400
        if len(content) > 5000:  # Maximum length
            return "Job description too long", 400
            
        return None, None 