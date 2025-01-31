from datetime import datetime, UTC
from openai import OpenAI
import os
import json
from app.response_template.resume_schema import RESUME_TEMPLATE
from app.response_template.analysis_schema import ANALYSIS_TEMPLATE

class ResumeAI:
    def __init__(self, extracted_text: str):
        """Initialize an AI-processed resume instance"""
        self.extracted_text = extracted_text
        self.parsed_resume = None
        self.analysis = None
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.timestamp = datetime.now(UTC).isoformat()
        self.resume_id = None

    def parse(self) -> dict:
        """Parse resume text into structured format using OpenAI"""
        prompt = f"""
        Please analyze this resume text and fill in the data according to this structure:
        {json.dumps(RESUME_TEMPLATE, indent=2)}

        Important instructions:
        1. Follow the exact schema structure
        2. Create as many entries in arrays as found in the resume
        3. Use "YYYY-MM" format for all dates
        4. Required fields must be filled
        5. Leave optional fields empty if not found in resume

        Resume text:
        {self.extracted_text}

        Return only the filled JSON structure.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", 
                     "content": "You are a precise resume parser that extracts structured data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Get content
            content = response.choices[0].message.content
            
            # Remove markdown wrapper
            cleaned_content = content.replace("```json", "").replace("```", "").strip()
            
            # Store the parsed result
            self.parsed_resume = json.loads(cleaned_content)
            return self.parsed_resume
            
        except Exception as e:
            raise Exception(f"Resume parsing failed: {str(e)}")

    def analyze(self, job_description: str) -> dict:
        """Analyze the parsed resume against job description"""
        if not self.parsed_resume:
            self.parse()  # Parse first if not already parsed
        
        prompt = f"""
        Analyze this resume against the job description and provide analysis according to this structure:
        {json.dumps(ANALYSIS_TEMPLATE, indent=2)}

        Resume Data:
        {json.dumps(self.parsed_resume, indent=2)}
        
        Job Description:
        {job_description}
        
        Important instructions:
        1. Follow the exact analysis schema structure
        2. Score each section from 0-100
        3. Provide detailed comments for each section
        4. Match each work experience, education, and project entry from the resume
        
        Return only the filled analysis structure.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert resume analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Clean and parse response
            content = response.choices[0].message.content
            cleaned_content = content.replace("```json", "").replace("```", "").strip()
            
            # Store and return the analysis
            self.analysis = json.loads(cleaned_content)
            return self.analysis
            
        except Exception as e:
            raise Exception(f"Resume analysis failed: {str(e)}")

    def process(self, job_description: str = None) -> dict:
        """Complete end-to-end AI resume processing"""
        try:
            # Step 1: Parse the resume
            self.parsed_resume = self.parse()
            
            # Step 2: Analyze against job description (if provided)
            if job_description:
                self.analysis = self.analyze(job_description)
            
            # Step 3: Return complete results
            result = {
                "resume_id": self.resume_id,
                "timestamp": self.timestamp,
                "parsed_resume": self.parsed_resume,
                "analysis": self.analysis if job_description else None
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Resume processing failed: {str(e)}")

    def process_section_feedback(self, section: str, subsection_data: dict, feedback: str = "") -> dict:
        """Process feedback and generate improved content for a specific section"""
        prompt = f"""
        Improve this resume section based on the feedback.
        
        Section Type: {section}
        Current Content: {json.dumps(subsection_data, indent=2)}
        User Feedback: {feedback if feedback else "Make this content more impactful and professional"}
        
        Please rewrite the content to address the feedback and improve its impact.
        If it's a description field, maintain bullet point format.
        Focus on being specific, quantifiable, and achievement-oriented.
        
        Return only the improved content in this JSON format:
        {{
            "Content": "improved content here"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert resume writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            cleaned_content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_content)
            
        except Exception as e:
            raise Exception(f"Failed to process section feedback: {str(e)}") 