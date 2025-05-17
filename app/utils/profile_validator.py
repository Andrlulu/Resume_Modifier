from flask import Request, jsonify
from app.models.temp import User

class ProfileValidator:
    @staticmethod
    def validate_profile_data(data: dict, user_id: int):
        """Validate profile update data"""
        if not data:
            return False, "Missing request data", 400
            
        # Check email uniqueness if being updated
        if 'email' in data:
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing_user:
                return False, "Email already in use", 400
                
        return True, data, 200 