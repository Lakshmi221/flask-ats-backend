import json
from openai import OpenAI
from src.config import config

class ATSScorer:
    """Class for calculating ATS scores and providing feedback"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from config"""
        self.client = OpenAI(api_key=config.openai_api_key)
    
    def calculate_score(self, resume_text, job_description):
        """
        Calculate ATS score and provide feedback
        
        Args:
            resume_text: Plain text of the resume
            job_description: Job description to compare against
            
        Returns:
            dict: ATS score and feedback
        """
        ats_prompt = """
        Analyze this resume against the job description and provide:
        
        1. An ATS compatibility score from 0-100
        2. Keyword match analysis (which important keywords are present and which are missing)
        3. Specific suggestions to improve the resume for this job
        4. Overall strengths and weaknesses
        
        Format the response as a valid JSON object with these fields: 
        "ats_score", "keyword_matches", "missing_keywords", "suggestions", "strengths", "weaknesses"
        
        Resume:
        ###
        {resume_text}
        ###
        
        Job Description:
        ###
        {job_description}
        ###
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert ATS scoring system that analyzes resumes."},
                    {"role": "user", "content": ats_prompt.format(
                        resume_text=resume_text, 
                        job_description=job_description
                    )}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error calculating ATS score: {str(e)}")
            raise