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
                model="gpt-4o",
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
                model="gpt-4o",
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
