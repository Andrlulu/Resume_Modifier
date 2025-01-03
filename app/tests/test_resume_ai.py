from app.services.resume_ai import ResumeAI
import os
import json

def test_resume_ai_init():
    """Test basic initialization of ResumeAI"""
    # Create a simple test text
    test_text = "John Doe\nSoftware Engineer"
    
    # Create an instance of ResumeAI
    resume = ResumeAI(test_text)
    
    # Check if text was stored correctly
    assert resume.extracted_text == test_text 

def test_resume_ai_attributes():
    """Test all initial attributes are set correctly"""
    test_text = "John Doe\nSoftware Engineer"
    resume = ResumeAI(test_text)
    
    # Check all initial attributes
    assert resume.parsed_resume is None
    assert resume.analysis is None
    assert resume.client is not None
    assert resume.timestamp is not None
    assert resume.resume_id is None 

def test_resume_parse():
    """Test parsing a simple resume"""
    test_text = """
    John Doe
    Software Engineer
    Email: john@example.com
    
    Experience:
    Google - Senior Developer
    2020-01 to Present
    - Led team of 5 developers
    - Implemented new features
    """
    
    resume = ResumeAI(test_text)
    parsed = resume.parse()
    
    # Check basic structure
    assert parsed is not None
    assert "userInfo" in parsed
    assert parsed["userInfo"]["firstName"] == "John"
    assert parsed["userInfo"]["lastName"] == "Doe"
    assert parsed["userInfo"]["email"] == "john@example.com" 

def test_resume_parse_raw():
    """Test parsing raw resume text from PDF"""
    # Read test resume from file
    test_file = os.path.join(os.path.dirname(__file__), 'test_data/sample_resume.txt')
    with open(test_file, 'r') as f:
        test_resume = f.read().strip()
    
    print("\nInput Resume Text:")
    print("="*80)
    print(test_resume)
    print("="*80)
    
    # Create instance and parse
    resume = ResumeAI(test_resume)
    parsed = resume.parse()
    
    # Print the parsed resume structure
    print("\nParsed Resume Structure:")
    print("="*80)
    print(json.dumps(parsed, indent=2))
    print("="*80)
    
    # Verify it's stored in the instance
    assert resume.parsed_resume is not None
    assert resume.parsed_resume == parsed
    
    # Test basic structure
    assert "userInfo" in parsed
    assert "workExperience" in parsed
    assert "education" in parsed
    
    # Test user info
    assert parsed["userInfo"]["firstName"] == "Homer"
    assert parsed["userInfo"]["lastName"] == "Simpson"
    assert parsed["userInfo"]["email"] == "Homer.Simpson@email.com"
    assert parsed["userInfo"]["phoneNumber"] == "(555) 555-5555"
    
    # Test education
    edu = parsed["education"][0]
    assert edu["institutionName"] == "University of Springfield"
    assert "Bachelor of Business Administration" in edu["degree"]
    assert edu["grade"] == "3.5"
    
    # Test work experience
    work = parsed["workExperience"][0]  # Most recent job
    assert work["companyName"] == "Springfield Inn"
    assert work["jobTitle"] == "Night Auditor"
    assert work["fromDate"] == "2017-05"
    assert work["toDate"] == "" 
    assert work["isPresent"] == True

def test_resume_analysis():
    """Test analyzing resume against job description"""
    # Read test resume from file
    test_file = os.path.join(os.path.dirname(__file__), 'test_data/sample_resume.txt')
    with open(test_file, 'r') as f:
        test_resume = f.read().strip()
    
    # Test job description for Night Auditor position
    test_job = """
    Night Auditor Position
    
    Requirements:
    - Bachelor's degree in Accounting or Business Administration
    - Experience with financial reporting and auditing
    - Ability to work independently during night shifts
    - Strong attention to detail with cash handling
    - Experience with end-of-day reporting
    
    Responsibilities:
    - Audit and balance daily reports
    - Manage end-of-day operations
    - Handle cash drawer reconciliation
    - Coordinate with other departments
    - Work independently during night shift
    """
    
    # Create instance and analyze
    resume = ResumeAI(test_resume)
    analysis = resume.analyze(test_job)
    
    # Print for review
    print("\nAnalysis Result:")
    print("="*80)
    print(json.dumps(analysis, indent=2))
    print("="*80)
    
    # Test structure matches ANALYSIS_TEMPLATE
    assert "overallAnalysis" in analysis
    assert "workExperience" in analysis
    assert "education" in analysis
    
    # Test overall analysis
    assert isinstance(analysis["overallAnalysis"]["score"], int)
    assert 0 <= analysis["overallAnalysis"]["score"] <= 100
    assert analysis["overallAnalysis"]["comment"] != ""
    
    # Test work experience analysis
    work = analysis["workExperience"][0]  # Current job
    assert work["companyName"] == "Springfield Inn"
    assert work["jobTitle"] == "Night Auditor"
    assert isinstance(work["score"], int)
    assert work["comment"] != ""
    
    # Test education analysis
    edu = analysis["education"][0]
    assert edu["institutionName"] == "University of Springfield"
    assert "Bachelor of Business Administration" in edu["degree"]
    assert isinstance(edu["score"], int)
    assert edu["comment"] != ""

def test_resume_process():
    """Test complete resume processing"""
    # Read test resume
    test_file = os.path.join(os.path.dirname(__file__), 'test_data/sample_resume.txt')
    with open(test_file, 'r') as f:
        test_resume = f.read().strip()
    
    # Test job description
    test_job = """
    Night Auditor Position
    
    Requirements:
    - Bachelor's degree in Accounting or Business Administration
    - Experience with financial reporting and auditing
    - Ability to work independently during night shifts
    - Strong attention to detail with cash handling
    - Experience with end-of-day reporting
    """
    
    # Create instance and process
    resume = ResumeAI(test_resume)
    result = resume.process(test_job)
    
    # Print complete result
    print("\nComplete Processing Result:")
    print("="*80)
    print(json.dumps(result, indent=2))
    print("="*80)
    
    # Test structure
    assert "resume_id" in result
    assert "timestamp" in result
    assert "parsed_resume" in result
    assert "analysis" in result
    
    # Test parsed resume
    parsed = result["parsed_resume"]
    assert parsed["userInfo"]["firstName"] == "Homer"
    assert parsed["userInfo"]["lastName"] == "Simpson"
    
    # Test analysis
    analysis = result["analysis"]
    assert analysis["overallAnalysis"]["score"] >= 0
    assert analysis["workExperience"][0]["companyName"] == "Springfield Inn"
    
    # Test without job description
    result_no_job = resume.process()
    assert result_no_job["analysis"] is None
