import json
from openai import OpenAI
from datetime import datetime
from src.config import config


class ResumeAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key)

    def clean_resume_text(self, resume_text):
        """Clean resume text to avoid content safety issues"""
        # Remove potential problematic characters or patterns
        import re
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', resume_text)
        
        # Remove potential problematic symbols
        cleaned = re.sub(r'[^\w\s\-\.\@\(\)\+\,\:\;\n]', '', cleaned)
        
        # Truncate if too long (OpenAI has token limits)
        if len(cleaned) > 10000:
            cleaned = cleaned[:10000]
        
        return cleaned.strip()

    def try_with_minimal_text(self, resume_text, job_description):
        """Fallback method with minimal text to avoid content filters"""
        
        # Extract only essential information
        lines = resume_text.split('\n')
        essential_lines = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['name', 'email', '@', 'phone', 'education', 'experience', 'skill', 'work', 'job', 'company']):
                essential_lines.append(line)
        
        minimal_text = '\n'.join(essential_lines[:50])  # Limit to first 50 relevant lines
        
        simple_prompt = f"""
Please extract basic information from this resume:

{minimal_text}

Return JSON with: candidate_name, Email, Phone, highest_education, skills, experience
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract resume information as JSON."},
                    {"role": "user", "content": simple_prompt}
                ],
                temperature=0
            )
            
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
            
        except Exception as e:
            print(f"Fallback method failed: {e}")
        
        return {}

    def extract_information(self, resume_text, job_description):
        """
        Step 1: Extract structured resume info including job experience (no calculations yet)
        """
        
        # Clean the resume text first
        cleaned_resume = self.clean_resume_text(resume_text)
        cleaned_job_desc = self.clean_resume_text(job_description)
        
        extraction_prompt = f"""
I need to extract professional information from a resume document for recruitment purposes.

Please extract the following structured information from the resume text below:

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

Resume Text:
{cleaned_resume}

Please format your entire response as valid JSON with the exact field names above.
"""

        try:
            # Try different models in order of preference
            models_to_try = ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
            
            for model in models_to_try:
                try:
                    print(f"Trying model: {model}")
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant that extracts structured information from professional resumes for recruitment purposes. Return only valid JSON."
                            },
                            {"role": "user", "content": extraction_prompt}
                        ],
                        response_format={"type": "json_object"} if model in ["gpt-4o", "gpt-4o-mini"] else None,
                        temperature=0.1
                    )
                    
                    # Check if this model worked
                    if response.choices and response.choices[0].message.content:
                        print(f"Success with model: {model}")
                        break
                    else:
                        print(f"Model {model} returned empty content")
                        continue
                        
                except Exception as model_error:
                    print(f"Model {model} failed: {model_error}")
                    continue
            else:
                print("All models failed")
                return {}
            
            # Add debugging prints
            print("Response status:", response)
            
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                print(f"Choice finish_reason: {choice.finish_reason}")
                print(f"Choice message: {choice.message}")
                
                # Check for refusal
                if hasattr(choice.message, 'refusal') and choice.message.refusal:
                    print(f"API Refusal: {choice.message.refusal}")
                    print("This indicates content safety filters were triggered")
                    print("Resume text length:", len(cleaned_resume))
                    print("Job description length:", len(cleaned_job_desc))
                    # Try with even more cleaned text
                    return self.try_with_minimal_text(cleaned_resume, cleaned_job_desc)
                
                content = choice.message.content
                print("Content:", content)
                
                if content is None:
                    print("Error: Content is None")
                    return {}
                
                try:
                    result = json.loads(content)
                    print("Parsed result:", result)
                except json.JSONDecodeError as json_err:
                    print(f"JSON decode error: {json_err}")
                    print(f"Raw content: {repr(content)}")
                    return {}
            else:
                print("Error: No choices in response")
                return {}

            # Proceed to step 2: GPT-based experience calculation
            result = self.evaluate_experience_with_gpt(result, job_description)

            return result

        except Exception as e:
            print(f"Error during GPT extraction: {e}")
            print(f"Error type: {type(e)}")
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

            # Add similar error checking here
            if not response.choices or response.choices[0].message.content is None:
                print("Error: No content in experience evaluation response")
                return extracted_data

            content = response.choices[0].message.content
            try:
                experience_result = json.loads(content)
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error in experience evaluation: {json_err}")
                return extracted_data

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