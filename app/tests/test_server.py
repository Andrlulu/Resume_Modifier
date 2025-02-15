import pytest
from app.server import app
import os
from dotenv import load_dotenv
import io
from app.extensions import db
from app.models.user import User
from sqlalchemy import text

load_dotenv()  # Load environment variables for tests too

@pytest.fixture
def client():
    """Test client fixture for Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(autouse=True)
def setup_test_database():
    """Setup/cleanup for tests without affecting production data"""
    with app.app_context():
        # First clean up any existing test data
        try:
            # Delete resumes first (due to foreign key constraint)
            db.session.execute(text('DELETE FROM resumes WHERE user_id IN (SELECT id FROM users WHERE email LIKE \'%@example.com\')'))
            # Then delete test users
            db.session.execute(text('DELETE FROM users WHERE email LIKE \'%@example.com\''))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Cleanup error: {e}")

        yield  # Run the test

        # Clean up after test
        try:
            # Delete resumes first (due to foreign key constraint)
            db.session.execute(text('DELETE FROM resumes WHERE user_id IN (SELECT id FROM users WHERE email LIKE \'%@example.com\')'))
            # Then delete test users
            db.session.execute(text('DELETE FROM users WHERE email LIKE \'%@example.com\''))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Cleanup error: {e}")

def test_pdf_upload(client):
    """Test PDF upload and parsing"""
    # Get test PDF path
    test_file = os.path.join(os.path.dirname(__file__), 'test_data/sample_resume.pdf')
    
    with open(test_file, 'rb') as pdf:
        data = {}
        data['file'] = (pdf, 'sample_resume.pdf')
        
        # Make request
        response = client.post(
            '/api/pdfupload',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Print full response and error details
        print("\nStatus Code:", response.status_code)
        print("Response Data:", response.get_json())
        
        # Original assertions
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 200
        assert 'data' in json_data
    
    # Check parsed resume structure
    parsed = json_data['data']
    assert 'userInfo' in parsed
    assert parsed['userInfo']['firstName'] == 'Homer'
    assert parsed['userInfo']['lastName'] == 'Simpson'
    assert 'workExperience' in parsed
    assert parsed['workExperience'][0]['companyName'] == 'Springfield Inn'

def test_job_description_upload(client):
    """Test job description analysis"""
    # First get parsed resume data
    test_file = os.path.join(os.path.dirname(__file__), 'test_data/sample_resume.pdf')
    
    with open(test_file, 'rb') as pdf:
        data = {}
        data['file'] = (pdf, 'sample_resume.pdf')
        response = client.post('/api/pdfupload', 
                             data=data, 
                             content_type='multipart/form-data')
        parsed_resume = response.get_json()['data']
    
    # Now test job description analysis
    job_data = {
        "updated_resume": parsed_resume,
        "job_description": """
        Night Auditor Position
        Requirements:
        - Bachelor's degree in Accounting or Business Administration
        - Experience with financial reporting and auditing
        - Ability to work independently during night shifts
        """
    }
    
    response = client.post(
        '/api/job_description_upload',
        json=job_data,
        content_type='application/json'
    )
    
    # Check response
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 200
    assert 'data' in json_data
    
    # Check analysis structure
    analysis = json_data['data']
    assert 'overallAnalysis' in analysis
    assert 'workExperience' in analysis
    assert analysis['workExperience'][0]['companyName'] == 'Springfield Inn'

def test_process_feedback(client):
    """Test processing feedback for a specific section"""
    # First upload a resume to establish session
    test_file = os.path.join(os.path.dirname(__file__), 'test_data/sample_resume.pdf')
    with open(test_file, 'rb') as pdf:
        data = {}
        data['file'] = (pdf, 'sample_resume.pdf')
        client.post('/api/pdfupload', data=data, content_type='multipart/form-data')
    
    # Test data for feedback request
    feedback_data = {
        "section": {
            "section type": "workExperience",
            "companyName": "Springfield Inn",
            "jobTitle": "Night Auditor",
            "description": "• Managed end-of-day operations and financial reporting"
        },
        "feedback": "Need more emphasis on leadership skills",
        "updated_resume": {
            "workExperience": [
                {
                    "companyName": "Springfield Inn",
                    "jobTitle": "Night Auditor",
                    "description": "• Managed end-of-day operations and financial reporting"
                }
            ]
        }
    }
    
    # Make feedback request
    response = client.put(
        '/api/feedback',
        json=feedback_data,
        content_type='application/json'
    )
    
    # Print response for debugging
    print("\nFeedback Response Status:", response.status_code)
    print("Feedback Response:", response.get_json())
    
    # Test response
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 200
    assert 'data' in json_data
    
    # Test content structure
    data = json_data['data']
    assert 'Content' in data
    assert isinstance(data['Content'], str)
    assert len(data['Content']) > 0

def test_register(client):
    """Test user registration"""
    # Test data
    user_data = {
        "email": "test_register@example.com",
        "password": "testpassword123"
    }
    
    # Make register request
    response = client.post(
        '/api/register',
        json=user_data,
        content_type='application/json'
    )
    
    # Print response for debugging
    print("\nRegister Response Status:", response.status_code)
    print("Register Response:", response.get_json())
    
    # Test response
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['status'] == 201
    assert 'user' in json_data
    assert json_data['user']['email'] == user_data['email']

def test_login(client):
    """Test user login"""
    # First register a user
    user_data = {
        "email": "test_login@example.com",
        "password": "testpassword123"
    }
    register_response = client.post('/api/register', json=user_data, content_type='application/json')
    assert register_response.status_code == 201
    
    # Test login
    response = client.post(
        '/api/login',
        json=user_data,
        content_type='application/json'
    )
    
    # Print response for debugging
    print("\nLogin Response Status:", response.status_code)
    print("Login Response:", response.get_json())
    
    # Test response
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == "success"
    assert 'user' in json_data
    assert json_data['user']['email'] == user_data['email']

def test_invalid_login(client):
    """Test login with invalid credentials"""
    # Test data
    user_data = {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }
    
    # Make login request
    response = client.post(
        '/api/login',
        json=user_data,
        content_type='application/json'
    )
    
    # Test response
    assert response.status_code == 401
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == "Invalid email or password" 