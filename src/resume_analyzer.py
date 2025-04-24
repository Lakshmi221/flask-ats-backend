import json
from openai import OpenAI
from src.config import config

class ResumeAnalyzer:
    """Class for extracting structured information from resumes"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from config"""
        self.client = OpenAI(api_key=config.openai_api_key)
    
    def extract_information(self, resume_text):
        """
        Extract structured information from a resume
        
        Args:
            resume_text: Plain text of the resume
            
        Returns:
            dict: Structured resume information
        """
        extraction_prompt = """
        Extract the following information from the resume in a structured JSON format:
        
        1. Full Name
        2. Email
        3. Phone Number
        4. LinkedIn URL (if available)
        5. Education (list of degrees, institutions, dates, and GPA if available)
        6. Skills (technical and soft skills)
        7. Work Experience (list of positions with company names, dates, and responsibilities)
        8. Projects (if available)
        9. Certifications (if available)
        10. Languages (if available)
        
        Format the response as a valid JSON object with these fields.
        
        Resume Text:
        ###
        {resume_text}
        ###
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a precise resume parser that extracts structured information."},
                    {"role": "user", "content": extraction_prompt.format(resume_text=resume_text)}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error extracting resume information: {str(e)}")
            raise