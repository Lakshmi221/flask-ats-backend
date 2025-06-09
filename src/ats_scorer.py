import json
from openai import OpenAI
from src.config import config

class ATSScorer:
    """Class for calculating ATS scores against job descriptions"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from config"""
        self.client = OpenAI(api_key=config.openai_api_key)
    
    def calculate_score(self, resume_text, job_description, relevant_years_experience=None):
        """
        Calculate ATS score and match percentages
        
        Args:
            resume_text: Plain text of the resume
            job_description: Job description to compare against
            relevant_years_experience: Optional pre-extracted years of relevant experience
            
        Returns:
            dict: Match percentages and skills analysis
        """
        # Determine relevant years text for prompt
        years_text = ""
        if relevant_years_experience is not None:
            years_text = f"The candidate has {relevant_years_experience} years of relevant experience."
        
        # Note: Using raw string to avoid f-string formatting issues with JSON example
        ats_prompt = f"""
        You are an expert ATS (Applicant Tracking System) analyzer tasked with evaluating a resume against a specific job description.
        
        Your analysis must be thorough, detail-oriented, and completely deterministic. For the same resume and job description, 
        you must return identical scores every time. Follow these precise analytical steps:
        
        STEP 1: Thoroughly analyze the job description to identify:
        - Required technical skills (hard skills)
        - Required soft skills
        - Required years of experience
        - Required education level
        - Key responsibilities
        - Industry-specific keywords
        - Primary technologies mentioned
        
        STEP 2: Analyze the resume to extract:
        - Present skills (both explicit and implied)
        - Years of experience (total and by role)
        - Education qualifications
        - Past responsibilities and achievements
        - Domain expertise
        {years_text}
        
        STEP 3: Conduct a systematic comparison:
        - Match each required skill against skills in the resume
        - Compare experience levels to requirements
        - Evaluate education qualifications against requirements
        - Identify keyword matches and gaps
        
        STEP 4: Calculate percentage scores based on these strict criteria:
        - For skills_match_percentage: (number of matching skills / total required skills) * 100
        - For experience_match_percentage: Compare years and relevance of experience to requirements
        - For education_match_percentage: Compare education level and relevance to requirements
        - For overall_match_percentage: Weighted average with higher weight to skills and experience
        
        STEP 5: Output ONLY the following fields as a valid JSON object:
        - overall_match_percentage: Numerically precise match percentage (0-100)
        - skills_match_percentage: Numerically precise skills match percentage (0-100)
        - experience_match_percentage: Numerically precise experience match percentage (0-100)
        - education_match_percentage: Numerically precise education match percentage (0-100)
        - matched_skills: Array of skills found in both resume and job description
        - missing_skills: Array of important skills mentioned in job description but not in resume
        
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
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a precise ATS scoring system that evaluates resumes against job descriptions with complete determinism. You must output valid JSON with only the exact field names requested: overall_match_percentage, skills_match_percentage, experience_match_percentage, education_match_percentage, matched_skills, missing_skills."},
                    {"role": "user", "content": ats_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0  # Setting temperature to 0 for maximum determinism
            )
            
            # Parse the response JSON
            result = json.loads(response.choices[0].message.content)
            
            # Ensure all required fields are present
            required_fields = [
                "overall_match_percentage", "skills_match_percentage", "experience_match_percentage",
                "education_match_percentage", "matched_skills", "missing_skills"
            ]
            
            for field in required_fields:
                if field not in result:
                    if field in ["matched_skills", "missing_skills"]:
                        result[field] = []
                    else:
                        result[field] = 0
            
            return result
            
        except Exception as e:
            print(f"Error calculating ATS score: {str(e)}")
            raise