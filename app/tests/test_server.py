import pytest
from app.server import app
import os
from dotenv import load_dotenv
import io

load_dotenv()  # Load environment variables for tests too

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Use the same secret key from environment
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
    with app.test_client() as client:
        yield client

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
    # First upload a resume - Use PDF file like in first test
    test_file = os.path.join(os.path.dirname(__file__), 'test_data/sample_resume.pdf')
    
    with open(test_file, 'rb') as pdf:
        data = {}
        data['file'] = (pdf, 'sample_resume.pdf')
        client.post('/api/pdfupload', data=data, content_type='multipart/form-data')
    
    # Now upload job description
    job_text = """
    Night Auditor Position
    Requirements:
    - Bachelor's degree in Accounting or Business Administration
    - Experience with financial reporting and auditing
    - Ability to work independently during night shifts
    """
    job_content = io.BytesIO(job_text.encode('utf-8'))
    
    data = {}
    data['file'] = (job_content, 'job.txt')
    
    response = client.post(
        '/api/job_description_upload',
        data=data,
        content_type='multipart/form-data'
    )
    
    # Print response for debugging
    print("\nJob Analysis Status Code:", response.status_code)
    print("Job Analysis Response:", response.get_json())
    
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