from flask import Blueprint, request, jsonify
from app.extensions import db
from app.utils.pdf_validator import PDFValidator
from app.utils.job_validator import JobValidator
from app.utils.parse_pdf import parse_pdf_file
from app.services.resume_ai import ResumeAI
from app.response_template.resume_schema import RESUME_TEMPLATE
from app.models.temp import User, Resume, JobDescription
from app.utils.feedback_validator import FeedbackValidator
from app.utils.jwt_utils import generate_token, token_required
from app.utils.profile_validator import ProfileValidator
import datetime

# Create blueprint
api = Blueprint('api', __name__)

@api.route('/')
def index():
    return "Flask App is Running!"

@api.route('/api/pdfupload', methods=['POST'])
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
        
        return jsonify({
            "status": 200,
            "data": parsed_resume
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Resume processing failed", 
            "details": str(e)
        }), 500

@api.route('/api/job_description_upload', methods=['POST'])
def analyze_with_job():
    """Analyze resume with job description"""
    # Validate request
    error, status_code, data = JobValidator.validate_request(request)
    if error:
        return error, status_code
    
    try:
        # Process with ResumeAI
        resume_processor = ResumeAI("")  # Empty string as we're using provided resume
        resume_processor.parsed_resume = data['updated_resume']
        analysis = resume_processor.analyze(data['job_description'])

        return jsonify({
            "status": 200,
            "data": analysis
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Analysis failed",
            "details": str(e)
        }), 500

@api.route('/api/feedback', methods=['PUT'])
def process_feedback():
    """Process feedback and updated resume data."""
    # Validate request
    error, status_code, data = FeedbackValidator.validate_request(request)
    if error:
        return error, status_code
    
    try:
        # Extract fields from validated data
        section = data['section']
        feedback = data.get('feedback', '')
        updated_resume = data['updated_resume']
        
        # Process with ResumeAI
        resume_processor = ResumeAI("")  # Empty string as we're using provided resume
        resume_processor.parsed_resume = updated_resume
        
        # Process feedback for the specific section
        analysis = resume_processor.process_section_feedback(
            section=section['section type'],
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

@api.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
        
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
    
    # Create new user
    user = User(
        email=data['email'],
        username=data['email'],  # Use email as username if not provided
        updated_at=datetime.datetime.utcnow(),
        created_at=datetime.datetime.utcnow()
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "status": 201,
            "user": {"email": user.email}
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500

@api.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate input
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
        
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Generate token
    token = generate_token(user.id, user.email)
    
    return jsonify({
        "status": "success",
        "user": {"email": user.email},
        "token": token
    }), 200

@api.route('/api/save_resume', methods=['PUT'])
@token_required
def save_resume():
    """Save or update a resume for the user"""
    # Get user ID from token
    user_id = request.user.get('user_id')
    
    # Get and validate JSON data
    data = request.get_json()
    if not data or 'updated_resume' not in data:
        return jsonify({"error": "Missing resume data"}), 400
        
    # Get resume title from root level
    resume_title = data.get('resume_title')
    if not resume_title:
        return jsonify({"error": "Resume title is required"}), 400
    
    # Get template ID (required field)
    # template = data.get('template')
    # if template is None:
    #     return jsonify({"error": "Template ID is required"}), 400
    
    resume_data = data['updated_resume']
    
    try:
        # Check if resume with same title exists for this user
        existing_resume = Resume.query.filter_by(
            user_id=user_id,
            title=resume_title
        ).first()
        
        if existing_resume:
            # Update existing resume
            existing_resume.parsed_resume = resume_data
            # existing_resume.template = template
            existing_resume.template = 1
            db.session.commit()
        else:
            # Create new resume entry
            # Get the next serial number for this user
            existing_count = Resume.query.filter_by(user_id=user_id).count()
            now = datetime.datetime.now(datetime.UTC)  # Using timezone-aware datetime
            
            resume = Resume(
                user_id=user_id,
                serial_number=existing_count + 1,  # Increment from existing count
                title=resume_title,
                parsed_resume=resume_data,
                # template=template,
                template=1,
                updated_at=now,
                created_at=now
            )
            db.session.add(resume)
            db.session.commit()
        
        return jsonify({
            "status": 200,
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to save resume",
            "details": str(e)
        }), 500

@api.route('/api/get_resume_list', methods=['GET'])
@token_required
def get_resume_list():
    """Get list of resumes for the current user"""
    user_id = request.user.get('user_id')
    
    try:
        # Query resumes for this user
        resumes = Resume.query.filter_by(user_id=user_id).all()
        
        # Format response
        resume_list = [{
            "resume_id": resume.serial_number,
            "resume_title": resume.title,
            "created_at": resume.created_at.isoformat()
        } for resume in resumes]
        
        return jsonify({
            "status": 200,
            "data": resume_list
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch resume list",
            "details": str(e)
        }), 500

@api.route('/api/get_resume/<int:resume_id>', methods=['GET'])
@token_required
def get_resume(resume_id):
    """Get a specific resume by ID"""
    user_id = request.user.get('user_id')
    
    try:
        # Query resume and verify ownership
        resume = Resume.query.filter_by(
            serial_number=resume_id,
            user_id=user_id
        ).first()
        
        if not resume:
            return jsonify({
                "error": "Resume not found or access denied"
            }), 404
        
        return jsonify({
            "status": 200,
            "data": {
                "resume": resume.parsed_resume,
                "resume_title": resume.title
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch resume",
            "details": str(e)
        }), 500

@api.route('/api/put_profile', methods=['PUT'])
@token_required
def put_profile():
    """Update user profile"""
    user_id = request.user.get('user_id')
    
    # Validate request data
    valid, message, status_code = ProfileValidator.validate_profile_data(
        request.get_json(), 
        user_id
    )
    if not valid:
        return jsonify({"error": message}), status_code
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Update allowed fields
        fields = ['first_name', 'last_name', 'email', 'city', 'country', 'bio']
        for field in fields:
            if field in message:  # message contains validated data
                setattr(user, field, message[field])
            
        db.session.commit()
        return jsonify({
            "status": 200,
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to update profile",
            "details": str(e)
        }), 500
    

@api.route('/api/get_profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    user_id = request.user.get('user_id')
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "status": 200,
            "data": {
                "profile": {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "city": user.city,
                    "country": user.country,
                    "bio": user.bio
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch profile",
            "details": str(e)
        }), 500