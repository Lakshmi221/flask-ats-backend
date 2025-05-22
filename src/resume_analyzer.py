
# import json
# from openai import OpenAI
# from src.config import config
# from datetime import datetime

# class ResumeAnalyzer:
#     """Streamlined class for extracting key information from resumes with accurate experience calculation"""
    
#     def __init__(self):
#         """Initialize OpenAI client with API key from config"""
#         self.client = OpenAI(api_key=config.openai_api_key)
    
#     def extract_information(self, resume_text, job_description):

#         """
#         Extract only key information from resume text: name, email, phone, education, skills, and experience
        
#         Args:
#             resume_text: Plain text of the resume
#             job_description: Job description to compare against for relevant experience
            
#         Returns:
#             dict: Extracted key resume information with accurate experience calculations
#         """
#         current_date = datetime.now().strftime("%Y-%m-%d")
#         print(current_date)


#         # current_date = datetime.now().strftime("%Y-%m-%d")
#         extraction_prompt = """
#         Extract only the specifically requested information from this resume and provide a focused analysis.
        
#         The job description provided will help you determine relevant experience years.
        
#         Extract the following information and format it as a valid JSON object:
        
#         - candidate_name: The full name of the candidate (First and Last name)
#         - Email: The candidate's email address (exact format as shown in resume)
#         - Phone: The candidate's phone number with country code if available
#         - highest_education: The highest education qualification obtained with degree, field and institution
#         - skills: A comma-separated list of all technical and soft skills found in the resume
#         - total_experience_years: The total years of work experience (as a number with 1 decimal place, e.g., 4.5)
#         - relevant_experience_years: Years of experience relevant to the job description (as a number with 1 decimal place)
        
#         For calculating total experience:
#         1. Sum up all work experience years from all jobs listed in the resume
#         2. Handle gaps and overlaps properly
#         3. Convert months to decimal years (e.g., 6 months = 0.5 years)
#         4. Be precise about dates - use exact dates if available
#         5. IMPORTANT: For any position listed as "present" or "current", use today's date ({current_date}) as the end date
        
#         For calculating relevant experience:
#         1. Analyze the job description to identify key roles, skills, and domains
#         2. Only count experience years that align with the target role/domain in the job description
#         3. For partially relevant roles, estimate the percentage of relevance and calculate accordingly
        
#         Your response must be a properly formatted JSON object with EXACTLY these field names.
        
#         Example format:
#         {{
#             "candidate_name": "John Doe",
#             "Email": "john@example.com",
#             "Phone": "+1 123-456-7890",
#             "highest_education": "Master's in Computer Science from Stanford University",
#             "skills": ["Python, JavaScript, SQL, Machine Learning, Project Management, Communication"]
#             "total_experience_years": 8.5,
#             "relevant_experience_years": 5.5
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
#             # Call to get key resume information with relevant experience
#             response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": """You are an expert resume analyzer with experience in HR and recruitment. 
#                     You specialize in accurately extracting information from resumes and calculating precise work experience durations.
#                     You must output valid JSON with the exact field names requested and ensure all numerical values for experience are accurate
#                     by calculating actual months and years worked from the dates provided in the resume."""},
#                     {"role": "user", "content": extraction_prompt.format(
#                         resume_text=resume_text,
#                         job_description=job_description,
#                         current_date = current_date
#                     )}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             # Parse the response JSON
#             result = json.loads(response.choices[0].message.content)
            
#             # Verify experience calculations with a second check
#             verification_prompt = f"""
#             Review the following extracted information from a resume and verify that the experience calculations are accurate.
            
#             Current extracted information:
#             - Total Experience: {result.get("total_experience_years", "N/A")} years
#             - Relevant Experience: {result.get("relevant_experience_years", "N/A")} years

#             Given the job description and resume below, verify these calculations and correct them if needed.
#             Provide only the corrected values in this exact JSON format:
#             {{
#                 "total_experience_years": decimal_number,
#                 "relevant_experience_years": decimal_number
#             }}
            
#             Resume:
#             ###
#             {resume_text}
#             ###
            
#             Job Description:
#             ###
#             {job_description}
#             ###
#             """
            
#             # Verification call to double-check experience calculations
#             verification_response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert at verifying resume experience calculations with high precision."},
#                     {"role": "user", "content": verification_prompt}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             verification_result = json.loads(verification_response.choices[0].message.content)
            
#             # Update the original result with verified experience calculations
#             for key in verification_result:
#                 result[key] = verification_result[key]
            
#             # Ensure all required fields are present
#             required_fields = [
#                 "candidate_name", "Email", "Phone", "highest_education", 
#                 "skills", "total_experience_years", "relevant_experience_years"
#             ]
            
#             for field in required_fields:
#                 if field not in result:
#                     if field == "skills":
#                         result[field] = ""
#                     elif field in ["total_experience_years", "relevant_experience_years"]:
#                         result[field] = 0.0
#                     else:
#                         result[field] = ""
            
#             return result
            
#         except Exception as e:
#             print(f"Error extracting resume information: {str(e)}")
#             raise
            
#     def get_key_resume_data(self, resume_text, job_description):
#         """
#         Helper method to extract only the key fields needed
#         """
#         full_data = self.extract_information(resume_text, job_description)
        
#         # Return only the required fields
#         return {
#             "candidate_name": full_data.get("candidate_name", ""),
#             "Email": full_data.get("Email", ""),
#             "Phone": full_data.get("Phone", ""),
#             "highest_education": full_data.get("highest_education", ""),
#             "skills": full_data.get("skills", ""),
#             "total_experience_years": full_data.get("total_experience_years", 0.0),
#             "relevant_experience_years": full_data.get("relevant_experience_years", 0.0)
#         }


# import json
# import re
# from openai import OpenAI
# from src.config import config
# from datetime import datetime

# class ResumeAnalyzer:
#     """Streamlined class for extracting key information from resumes with accurate experience calculation"""
    
#     def __init__(self):
#         """Initialize OpenAI client with API key from config"""
#         self.client = OpenAI(api_key=config.openai_api_key)
    
#     def extract_information(self, resume_text, job_description):
#         """
#         Extract only key information from resume text: name, email, phone, education, skills, and experience
        
#         Args:
#             resume_text: Plain text of the resume
#             job_description: Job description to compare against for relevant experience
            
#         Returns:
#             dict: Extracted key resume information with accurate experience calculations
#         """
#         # Get current date for "present" calculations
#         current_date = datetime.now().strftime("%Y-%m-%d")
        
#         extraction_prompt = f"""
        # Extract only the specifically requested information from this resume and provide a focused analysis.
        
        # The job description provided will help you determine relevant experience years.
        
        # Extract the following information and format it as a valid JSON object:
        
        # - candidate_name: The full name of the candidate (First and Last name)
        # - Email: The candidate's email address (exact format as shown in resume)
        # - Phone: The candidate's phone number with country code if available
        # - highest_education: The highest education qualification obtained with degree, field and institution
        # - skills: A comma-separated list of all technical and soft skills found in the resume
        # - total_experience_years: The total years of work experience (as a number with 1 decimal place, e.g., 4.5)
        # - relevant_experience_years: Years of experience relevant to the job description (as a number with 1 decimal place)
        
        # For calculating total experience:
        # 1. Sum up all work experience years from all jobs listed in the resume
        # 2. Handle gaps and overlaps properly
        # 3. Convert months to decimal years (e.g., 6 months = 0.5 years)
        # 4. Be precise about dates - use exact dates if available
        # 5. IMPORTANT: For any position listed as "present" or "current", use today's date ({current_date}) as the end date
        
        # For calculating relevant experience:
        # 1. Analyze the job description to identify key roles, skills, and domains
        # 2. Only count experience years that align with the target role/domain in the job description
        # 3. For partially relevant roles, estimate the percentage of relevance and calculate accordingly
        
        # Your response must be a properly formatted JSON object with EXACTLY these field names.
        
        # Example format:
        # {{
        #     "candidate_name": "John Doe",
        #     "Email": "john@example.com",
        #     "Phone": "+1 123-456-7890",
        #     "highest_education": "Master's in Computer Science from Stanford University",
        #     "skills": "Python, JavaScript, SQL, Machine Learning, Project Management, Communication",
        #     "total_experience_years": 8.5,
        #     "relevant_experience_years": 5.5
        # }}
        
        # Resume:
        # ###
        # {resume_text}
        # ###
        
        # Job Description:
        # ###
        # {job_description}
        ###
#         """
        
#         try:
#             # Call to get key resume information with relevant experience
#             response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": """You are an expert resume analyzer with experience in HR and recruitment. 
#                     You specialize in accurately extracting information from resumes and calculating precise work experience durations.
#                     You must output valid JSON with the exact field names requested and ensure all numerical values for experience are accurate
#                     by calculating actual months and years worked from the dates provided in the resume."""},
#                     {"role": "user", "content": extraction_prompt.format(
#                         resume_text=resume_text,
#                         job_description=job_description
#                     )}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             # Parse the response JSON
#             result = json.loads(response.choices[0].message.content)
            
#             # Verify experience calculations with a second check
#             # Get current date for "present" calculations in verification step
#             current_date = datetime.now().strftime("%Y-%m-%d")
            
#             verification_prompt = f"""
#             Review the following extracted information from a resume and verify that the experience calculations are accurate.
            
#             Current extracted information:
#             - Total Experience: {result.get("total_experience_years", "N/A")} years
#             - Relevant Experience: {result.get("relevant_experience_years", "N/A")} years

#             Given the job description and resume below, verify these calculations and correct them if needed.
#             For any position listed as "present" or "current", use today's date ({current_date}) as the end date.
            
#             Provide only the corrected values in this exact JSON format:
#             {{
#                 "total_experience_years": decimal_number,
#                 "relevant_experience_years": decimal_number
#             }}
            
#             Resume:
#             ###
#             {resume_text}
#             ###
            
#             Job Description:
#             ###
#             {job_description}
#             ###
#             """
            
#             # Verification call to double-check experience calculations
#             verification_response = self.client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert at verifying resume experience calculations with high precision."},
#                     {"role": "user", "content": verification_prompt}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             verification_result = json.loads(verification_response.choices[0].message.content)
            
#             # Update the original result with verified experience calculations
#             for key in verification_result:
#                 result[key] = verification_result[key]
            
#             # Ensure all required fields are present
#             required_fields = [
#                 "candidate_name", "Email", "Phone", "highest_education", 
#                 "skills", "total_experience_years", "relevant_experience_years"
#             ]
            
#             for field in required_fields:
#                 if field not in result:
#                     if field == "skills":
#                         result[field] = ""
#                     elif field in ["total_experience_years", "relevant_experience_years"]:
#                         result[field] = 0.0
#                     else:
#                         result[field] = ""
            
#             return result
            
#         except Exception as e:
#             print(f"Error extracting resume information: {str(e)}")
#             raise
            
#     def calculate_experience_from_dates(self, start_date_str, end_date_str):
#         """
#         Calculate experience in years (with decimal precision) between two dates
        
#         Args:
#             start_date_str: String representation of start date (YYYY-MM-DD, YYYY-MM, or MM/YYYY)
#             end_date_str: String representation of end date or "Present"/"Current"
            
#         Returns:
#             float: Experience in years with 1 decimal place
#         """
#         try:
#             # Handle various date formats
#             start_date = None
#             end_date = None
            
#             # Process start date
#             if "-" in start_date_str:
#                 # Handle YYYY-MM-DD or YYYY-MM format
#                 parts = start_date_str.split("-")
#                 if len(parts) == 3:  # YYYY-MM-DD
#                     start_date = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
#                 elif len(parts) == 2:  # YYYY-MM
#                     start_date = datetime(int(parts[0]), int(parts[1]), 1)
#             elif "/" in start_date_str:
#                 # Handle MM/YYYY format
#                 parts = start_date_str.split("/")
#                 if len(parts) == 2:
#                     start_date = datetime(int(parts[1]), int(parts[0]), 1)
            
#             # Process end date
#             if end_date_str.lower() in ["present", "current", "now"]:
#                 end_date = datetime.now()
#             elif "-" in end_date_str:
#                 # Handle YYYY-MM-DD or YYYY-MM format
#                 parts = end_date_str.split("-")
#                 if len(parts) == 3:  # YYYY-MM-DD
#                     end_date = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
#                 elif len(parts) == 2:  # YYYY-MM
#                     end_date = datetime(int(parts[0]), int(parts[1]), 1)
#             elif "/" in end_date_str:
#                 # Handle MM/YYYY format
#                 parts = end_date_str.split("/")
#                 if len(parts) == 2:
#                     end_date = datetime(int(parts[1]), int(parts[0]), 1)
            
#             if start_date and end_date:
#                 # Calculate difference in years
#                 diff_years = (end_date - start_date).days / 365.25
#                 # Round to 1 decimal place
#                 return round(diff_years, 1)
#             else:
#                 return 0.0
                
#         except Exception as e:
#             print(f"Error calculating experience: {str(e)}")
#             return 0.0
    
#     def get_key_resume_data(self, resume_text, job_description):
#         """
#         Helper method to extract only the key fields needed
        
#         Args:
#             resume_text: Plain text of the resume
#             job_description: Job description to compare against for relevant experience
            
#         Returns:
#             dict: Key resume information with accurate experience calculations
#         """
#         try:
#             full_data = self.extract_information(resume_text, job_description)
            
#             # Return only the required fields
#             return {
#                 "candidate_name": full_data.get("candidate_name", ""),
#                 "Email": full_data.get("Email", ""),
#                 "Phone": full_data.get("Phone", ""),
#                 "highest_education": full_data.get("highest_education", ""),
#                 "skills": full_data.get("skills", ""),
#                 "total_experience_years": full_data.get("total_experience_years", 0.0),
#                 "relevant_experience_years": full_data.get("relevant_experience_years", 0.0)
#             }
#         except Exception as e:
#             print(f"Error in get_key_resume_data: {str(e)}")
#             # Return default values on error to prevent application crashes
#             return {
#                 "candidate_name": "",
#                 "Email": "",
#                 "Phone": "",
#                 "highest_education": "",
#                 "skills": "",
#                 "total_experience_years": 0.0,
#                 "relevant_experience_years": 0.0
#             }


import json
from openai import OpenAI
from datetime import datetime
from src.config import config


class ResumeAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key)

    def extract_information(self, resume_text, job_description):
        """
        Step 1: Extract structured resume info including job experience (no calculations yet)
        """

        extraction_prompt = f"""
Extract the following structured information from the resume below.
Use ONLY the content from the resume.

Return in JSON format with these exact fields:
- candidate_name
- Email
- Phone
- highest_education: Highest degree with institution
- skills: Comma-separated list
- experience: A list of entries in the format:
  {{
    "position": <Job Title>,
    "duration": <e.g., "March 2021 - Present">,
    "work": <What the candidate did in that role>
  }}

Resume:
###
{resume_text}
###

Only use the resume content. Format your entire response as valid JSON with the exact field names above.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a resume parser that returns clean, structured data in JSON. Only use content from the resume."
                    },
                    {"role": "user", "content": extraction_prompt}
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Proceed to step 2: GPT-based experience calculation
            result = self.evaluate_experience_with_gpt(result, job_description)

            return result

        except Exception as e:
            print(f"Error during GPT extraction: {e}")
            return {}

    def evaluate_experience_with_gpt(self, extracted_data, job_description):
        """
        Step 2: Ask GPT to compute total & relevant experience from experience list + job description
        """

        # Inject current date
        current_date = datetime.now().strftime("%B %Y")  # e.g., "May 2025"

        evaluation_prompt = f"""
You are an expert in evaluating professional experience from resumes.

Below is a list of job roles extracted from a candidate's resume. For any duration that mentions "present", "current", or similar, use today's date: **{current_date}** as the end date.

Analyze the positions, their durations, and work done in each role. Then:
- Calculate total experience in years (with 1 decimal)
- Calculate years of experience that are relevant to this job description (with 1 decimal)

Only return a JSON object in this format:
{{
  "total_experience_years": <decimal>,
  "relevant_experience_years": <decimal>
}}

Resume Experience:
{json.dumps(extracted_data.get("experience", []), indent=2)}

Job Description:
{job_description}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at interpreting resume experience and computing total and relevant years based on job descriptions."
                    },
                    {"role": "user", "content": evaluation_prompt}
                ],
                response_format={"type": "json_object"}
            )

            experience_result = json.loads(response.choices[0].message.content)

            extracted_data["total_experience_years"] = experience_result.get("total_experience_years", 0.0)
            extracted_data["relevant_experience_years"] = experience_result.get("relevant_experience_years", 0.0)

            return extracted_data

        except Exception as e:
            print(f"Error during GPT experience evaluation: {e}")
            return extracted_data

    def get_key_resume_data(self, resume_text, job_description):
        """
        Public method: returns extracted fields plus calculated experience
        """
        data = self.extract_information(resume_text, job_description)
        return {
            "candidate_name": data.get("candidate_name", ""),
            "Email": data.get("Email", ""),
            "Phone": data.get("Phone", ""),
            "highest_education": data.get("highest_education", ""),
            "skills": data.get("skills", ""),
            "experience": data.get("experience", []),
            "total_experience_years": data.get("total_experience_years", 0.0),
            "relevant_experience_years": data.get("relevant_experience_years", 0.0)
        }
