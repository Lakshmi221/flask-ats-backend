# import json
# from openai import OpenAI
# from src.config import config

# class ATSScorer:
#     """Class for calculating ATS scores and providing feedback"""
    
#     def __init__(self):
#         """Initialize OpenAI client with API key from config"""
#         self.client = OpenAI(api_key=config.openai_api_key)
    
#     def calculate_score(self, resume_text, job_description):
#         """
#         Calculate ATS score and provide feedback
        
#         Args:
#             resume_text: Plain text of the resume
#             job_description: Job description to compare against
            
#         Returns:
#             dict: ATS score and feedback
#         """
#         ats_prompt = """
#         Analyze this resume against the job description and provide:
        
#         1. An ATS compatibility score from 0-100
#         2. Keyword match analysis (which important keywords are present and which are missing)
#         3. Specific suggestions to improve the resume for this job
#         4. Overall strengths and weaknesses
        
#         Format the response as a valid JSON object with these fields: 
#         "ats_score", "keyword_matches", "missing_keywords", "suggestions", "strengths", "weaknesses"
        
#         Resume:
#         ###
#         {resume_text}
#         ###
        
#         Job Description:
#         ###
#         {job_description}
#         ###
#         """
        
#         try:
#             response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert ATS scoring system that analyzes resumes."},
#                     {"role": "user", "content": ats_prompt.format(
#                         resume_text=resume_text, 
#                         job_description=job_description
#                     )}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             return json.loads(response.choices[0].message.content)
#         except Exception as e:
#             print(f"Error calculating ATS score: {str(e)}")
#             raise



# import json
# from openai import OpenAI
# from src.config import config

# class ATSScorer:
#     """Class for calculating ATS scores and extracting relevant candidate information"""
    
#     def __init__(self):
#         """Initialize OpenAI client with API key from config"""
#         self.client = OpenAI(api_key=config.openai_api_key)
    
#     def calculate_score(self, resume_text, job_description):
#         """
#         Calculate ATS score and extract candidate information
        
#         Args:
#             resume_text: Plain text of the resume
#             job_description: Job description to compare against
            
#         Returns:
#             dict: Candidate details, match percentages, and extracted information
#         """
#         ats_prompt = """
#         Analyze this resume against the job description and provide a detailed analysis.
        
#         Extract the following information and format it as a valid JSON object:
        
#         - candidate_name: The full name of the candidate
#         - Email: The candidate's email address
#         - overall match percentage: A number representing the overall match with the job
#         - skills match percentage: A number representing the skills match with the job
#         - experience match percentage: A number representing the experience match with the job 
#         - skills: A comma-separated list of all skills found in the resume
#         - total years of relevant experience: The number of years of relevant experience
#         - total years experience: The number of years of total work experience
#         - highest education: The highest education qualification obtained
#         - matched skills: An array of skills that match the job requirements
#         - experience match: An array of relevant experience items that match job requirements
        
#         Your response must be a properly formatted JSON object with EXACTLY these field names.
        
#         Example format:
#         {{
#             "candidate_name": "John Doe",
#             "Email": "john@example.com",
#             "overall match percentage": "85",
#             "skills match percentage": "90",
#             "experience match percentage": "80",
#             "skills": "Python, JavaScript, SQL, Machine Learning",
#             "total years of relevant experience": "5",
#             "total years experience": "8",
#             "highest education": "Master's in Computer Science",
#             "matched skills": ["Python", "JavaScript", "SQL"],
#             "experience match": ["Backend Developer at XYZ Corp", "Data Analyst at ABC Inc"]
#         }}
        
#         Resume:
#         ###
#         {resume_text}
#         ###
        
#         Job Description:
#         ###
#         {job_description}
#         ###
#         """
        
#         try:
#             response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert ATS system that analyzes resumes and extracts relevant information. You must output valid JSON with the exact field names requested."},
#                     {"role": "user", "content": ats_prompt.format(
#                         resume_text=resume_text, 
#                         job_description=job_description
#                     )}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             # Parse the response JSON
#             result = json.loads(response.choices[0].message.content)
            
#             # Ensure all required fields are present
#             required_fields = [
#                 "candidate_name", "Email", "overall match percentage", 
#                 "skills match percentage", "experience match percentage", 
#                 "skills", "total years of relevant experience", "total years experience", 
#                 "highest education", "matched skills", "experience match"
#             ]
            
#             for field in required_fields:
#                 if field not in result:
#                     if field in ["matched skills", "experience match"]:
#                         result[field] = []
#                     else:
#                         result[field] = ""
            
#             return result
            
#         except Exception as e:
#             print(f"Error analyzing resume: {str(e)}")
#             raise
    
#     def get_improvement_suggestions(self, resume_text, job_description):
#         """
#         Get detailed suggestions for improving the resume
        
#         Args:
#             resume_text: Plain text of the resume
#             job_description: Job description to compare against
            
#         Returns:
#             dict: Suggestions for improvement
#         """
#         suggestion_prompt = """
#         Analyze this resume against the job description and provide specific suggestions for improvement.
        
#         Focus on:
#         1. Missing skills that would be valuable to add
#         2. Experience descriptions that could be enhanced
#         3. Format and presentation improvements
#         4. Keywords that should be emphasized
        
#         Format the response as a valid JSON object with these fields:
#         "missing_skills", "experience_improvements", "format_suggestions", "keyword_recommendations"
        
#         Resume:
#         ###
#         {resume_text}
#         ###
        
#         Job Description:
#         ###
#         {job_description}
#         ###
#         """
        
#         try:
#             response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert resume improvement system that provides actionable feedback."},
#                     {"role": "user", "content": suggestion_prompt.format(
#                         resume_text=resume_text, 
#                         job_description=job_description
#                     )}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             return json.loads(response.choices[0].message.content)
            
#         except Exception as e:
#             print(f"Error getting improvement suggestions: {str(e)}")
#             raise



# import json
# from openai import OpenAI
# from src.config import config

# class ResumeAnalyzer:
#     """Class for extracting information from resumes"""
    
#     def __init__(self):
#         """Initialize OpenAI client with API key from config"""
#         self.client = OpenAI(api_key=config.openai_api_key)
    
#     def extract_information(self, resume_text):
#         """
#         Extract detailed information from resume text
        
#         Args:
#             resume_text: Plain text of the resume
            
#         Returns:
#             dict: Extracted resume information
#         """
#         extraction_prompt = """
#         Extract detailed information from this resume and provide a comprehensive analysis.
        
#         Extract the following information and format it as a valid JSON object:
        
#         - candidate_name: The full name of the candidate
#         - Email: The candidate's email address
#         - Phone: The candidate's phone number
#         - Location: The candidate's location or address
#         - skills: A comma-separated list of all skills found in the resume
#         - total years experience: The number of years of total work experience
#         - highest education: The highest education qualification obtained
#         - certifications: List of certifications if any
#         - work_history: Array of work experiences with company name, position, duration, and responsibilities
#         - education_history: Array of education details with institution, degree, field of study, and graduation year
#         - projects: Array of projects with name, description, and technologies used
        
#         Your response must be a properly formatted JSON object with EXACTLY these field names.
        
#         Example format:
#         {{
#             "candidate_name": "John Doe",
#             "Email": "john@example.com",
#             "Phone": "123-456-7890",
#             "Location": "San Francisco, CA",
#             "skills": "Python, JavaScript, SQL, Machine Learning",
#             "total years experience": "8",
#             "highest education": "Master's in Computer Science",
#             "certifications": ["AWS Certified Solutions Architect", "PMP"],
#             "work_history": [
#                 {{
#                     "company": "XYZ Corp",
#                     "position": "Senior Developer",
#                     "duration": "2018-2023",
#                     "responsibilities": "Led development team, designed API architecture"
#                 }},
#                 {{
#                     "company": "ABC Inc",
#                     "position": "Software Engineer",
#                     "duration": "2015-2018",
#                     "responsibilities": "Developed web applications using React and Node.js"
#                 }}
#             ],
#             "education_history": [
#                 {{
#                     "institution": "Stanford University",
#                     "degree": "Master's",
#                     "field_of_study": "Computer Science",
#                     "graduation_year": "2015"
#                 }},
#                 {{
#                     "institution": "UC Berkeley",
#                     "degree": "Bachelor's",
#                     "field_of_study": "Computer Engineering",
#                     "graduation_year": "2013"
#                 }}
#             ],
#             "projects": [
#                 {{
#                     "name": "E-commerce Platform",
#                     "description": "Built a scalable e-commerce platform",
#                     "technologies": "React, Node.js, MongoDB"
#                 }},
#                 {{
#                     "name": "Data Analysis Tool",
#                     "description": "Created a tool for analyzing financial data",
#                     "technologies": "Python, Pandas, Matplotlib"
#                 }}
#             ]
#         }}
        
#         Resume:
#         ###
#         {resume_text}
#         ###
#         """
        
#         try:
#             response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert resume analyzer that extracts comprehensive information from resumes. You must output valid JSON with the exact field names requested."},
#                     {"role": "user", "content": extraction_prompt.format(resume_text=resume_text)}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             # Parse the response JSON
#             result = json.loads(response.choices[0].message.content)
            
#             # Ensure all required fields are present
#             required_fields = [
#                 "candidate_name", "Email", "Phone", "Location", "skills", 
#                 "total years experience", "highest education", "certifications", 
#                 "work_history", "education_history", "projects"
#             ]
            
#             for field in required_fields:
#                 if field not in result:
#                     if field in ["certifications", "work_history", "education_history", "projects"]:
#                         result[field] = []
#                     else:
#                         result[field] = ""
            
#             return result
            
#         except Exception as e:
#             print(f"Error extracting resume information: {str(e)}")
#             raise






# import json
# from openai import OpenAI
# from src.config import config

# class ATSScorer:
#     """Class for calculating ATS scores against job descriptions"""
    
#     def __init__(self):
#         """Initialize OpenAI client with API key from config"""
#         self.client = OpenAI(api_key=config.openai_api_key)
    
#     def calculate_score(self, resume_text, job_description):
#         """
#         Calculate ATS score and match percentages
        
#         Args:
#             resume_text: Plain text of the resume
#             job_description: Job description to compare against
            
#         Returns:
#             dict: Match percentages and relevance analysis
#         """
#         ats_prompt = """
#         Analyze this resume against the job description and provide an ATS scoring analysis.
        
#         Calculate and provide the following metrics as a valid JSON object:
        
#         - overall_match_percentage: A number representing the overall match with the job
#         - skills_match_percentage: A number representing the skills match with the job
#         - experience_match_percentage: A number representing the experience match with the job
#         - education_match_percentage: A number representing how well the education matches job requirements
#         - total_years_of_relevant_experience: The number of years of relevant experience related to this job
#         - matched_skills: An array of skills that match the job requirements
#         - missing_skills: An array of important skills mentioned in the job description but not found in the resume
#         - experience_match: An array of relevant experience items that match job requirements
#         - improvement_suggestions: An array of specific suggestions to improve the resume for this job
#         - keywords_missing: An array of important keywords from the job description not found in the resume
        
#         Your response must be a properly formatted JSON object with EXACTLY these field names.
        
#         Example format:
#         {{
#             "overall_match_percentage": 85,
#             "skills_match_percentage": 90,
#             "experience_match_percentage": 80,
#             "education_match_percentage": 100,
#             "total_years_of_relevant_experience": 5,
#             "matched_skills": ["Python", "JavaScript", "SQL"],
#             "missing_skills": ["AWS", "Docker"],
#             "experience_match": ["Backend Developer at XYZ Corp", "Data Analyst at ABC Inc"],
#             "improvement_suggestions": ["Add more AWS experience", "Quantify achievements with metrics"],
#             "keywords_missing": ["cloud infrastructure", "CI/CD pipeline"]
#         }}
        
#         Resume:
#         ###
#         {resume_text}
#         ###
        
#         Job Description:
#         ###
#         {job_description}
#         ###
#         """
        
#         try:
#             response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert ATS scoring system that evaluates resumes against job descriptions. You must output valid JSON with the exact field names requested."},
#                     {"role": "user", "content": ats_prompt.format(
#                         resume_text=resume_text, 
#                         job_description=job_description
#                     )}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             # Parse the response JSON
#             result = json.loads(response.choices[0].message.content)
            
#             # Ensure all required fields are present
#             required_fields = [
#                 "overall_match_percentage", "skills_match_percentage", "experience_match_percentage",
#                 "education_match_percentage", "total_years_of_relevant_experience",
#                 "matched_skills", "missing_skills", "experience_match", 
#                 "improvement_suggestions", "keywords_missing"
#             ]
            
#             for field in required_fields:
#                 if field not in result:
#                     if field in ["matched_skills", "missing_skills", "experience_match", 
#                                "improvement_suggestions", "keywords_missing"]:
#                         result[field] = []
#                     else:
#                         result[field] = 0
            
#             # Add candidate info from the original code to maintain compatibility
#             # These fields should be extracted by the ResumeAnalyzer now, but we're keeping
#             # them here for backward compatibility with existing frontend code
#             candidate_info = {
#                 "candidate_name": "",
#                 "Email": "",
#                 "skills": "",
#                 "total years experience": "",
#                 "highest education": ""
#             }
            
#             # Merge with the ATS result for compatibility
#             result.update(candidate_info)
            
#             return result
            
#         except Exception as e:
#             print(f"Error calculating ATS score: {str(e)}")
#             raise
    
#     def get_improvement_suggestions(self, resume_text, job_description):
#         """
#         Get detailed suggestions for improving the resume
        
#         Args:
#             resume_text: Plain text of the resume
#             job_description: Job description to compare against
            
#         Returns:
#             dict: Suggestions for improvement
#         """
#         suggestion_prompt = """
#         Analyze this resume against the job description and provide specific suggestions for improvement.
        
#         Focus on:
#         1. Missing skills that would be valuable to add
#         2. Experience descriptions that could be enhanced
#         3. Format and presentation improvements
#         4. Keywords that should be emphasized
        
#         Format the response as a valid JSON object with these fields:
#         "missing_skills", "experience_improvements", "format_suggestions", "keyword_recommendations"
        
#         Resume:
#         ###
#         {resume_text}
#         ###
        
#         Job Description:
#         ###
#         {job_description}
#         ###
#         """
        
#         try:
#             response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert resume improvement system that provides actionable feedback."},
#                     {"role": "user", "content": suggestion_prompt.format(
#                         resume_text=resume_text, 
#                         job_description=job_description
#                     )}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             return json.loads(response.choices[0].message.content)
            
#         except Exception as e:
#             print(f"Error getting improvement suggestions: {str(e)}")
#             raise



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
                model="gpt-4-turbo",
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