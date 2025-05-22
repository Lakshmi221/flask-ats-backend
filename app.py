# from flask import Flask, request, jsonify
# import os
# from werkzeug.utils import secure_filename

# # Import modules
# from src.config import config
# from src.s3_storage import S3Storage
# from src.mongodb_manager import MongoDBManager
# from src.pdf_extractor import PDFExtractor
# from src.resume_analyzer import ResumeAnalyzer
# from src.ats_scorer import ATSScorer

# from bson import ObjectId
# import json
# from json import JSONEncoder





# class MongoJSONEncoder(JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, ObjectId):
#             return str(obj)
#         return super(MongoJSONEncoder, self).default(obj)

# # Initialize Flask app
# app = Flask(__name__)

# # Configure upload folder
# app.config['UPLOAD_FOLDER'] = config.upload_folder

# # Create upload folder if it doesn't exist
# os.makedirs(config.upload_folder, exist_ok=True)

# def allowed_file(filename):
#     """Check if the file has an allowed extension"""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.allowed_extensions



# def convert_objectid_to_str(obj):
#     """
#     Recursively convert any ObjectId instances in a nested object to strings
#     """
#     if isinstance(obj, ObjectId):
#         return str(obj)
#     elif isinstance(obj, dict):
#         return {key: convert_objectid_to_str(value) for key, value in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_objectid_to_str(item) for item in obj]
#     return obj


# @app.route('/analyze-resume', methods=['POST'])
# def analyze_resume():
#     """
#     Endpoint to analyze a resume against a job description
    
#     Request should include:
#     - resume: PDF file
#     - job_description: Text of the job description
#     - userid: User ID for metadata
#     - name: User name for metadata
    
#     Returns:
#     - JSON with analysis results, including S3 URL and MongoDB ID
#     """
#     try:
#         # Check if the post request has the file part
#         if 'resume' not in request.files:
#             return jsonify({'error': 'No resume file provided'}), 400
        
#         file = request.files['resume']
        
#         job_description = request.form.get('job_description')
#         user_id = request.form.get('userid')
#         name = request.form.get('name')
        
#         metadata = {"userid": user_id, "name": name}
        
#         if not job_description:
#             return jsonify({'error': 'No job description provided'}), 400
        
#         if file.filename == '':
#             return jsonify({'error': 'No selected file'}), 400
        
#         if file and allowed_file(file.filename):
#             # Save the file temporarily
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
            
#             try:
#                 # Initialize services
#                 s3_storage = S3Storage()
#                 mongodb_manager = MongoDBManager()
#                 pdf_extractor = PDFExtractor()
#                 resume_analyzer = ResumeAnalyzer()
#                 ats_scorer = ATSScorer()
                
#                 # Extract text from PDF
#                 resume_text = pdf_extractor.extract_text(file_path)
#                 print("PDF text extracted successfully")
                
#                 # Upload to S3
#                 file_url = s3_storage.upload_resume(file_path, metadata)
                
#                 # Extract resume information
#                 resume_info = resume_analyzer.extract_information(resume_text)
#                 print("Resume information extracted")
                
#                 # Calculate ATS score
#                 ats_analysis = ats_scorer.calculate_score(resume_text, job_description)
#                 print("ATS analysis completed")
                
#                 # Combine all data
#                 result = {
#                     "resume_info": resume_info,
#                     "ats_analysis": ats_analysis,
#                     "file_url": file_url,
#                     "metadata": metadata,
#                     "job_description": job_description
#                 }
                
#                 # Save to MongoDB
#                 mongo_id = mongodb_manager.save_candidate_data(result)
                
#                 # Add MongoDB ID to result
#                 result["mongo_id"] = mongo_id
                
#                 # Convert any ObjectId instances in the result
#                 # Option 1: Using our custom function
#                 serializable_result = convert_objectid_to_str(result)
                
#                 # Clean up the temporary file
#                 if os.path.exists(file_path):
#                     os.remove(file_path)
                
#                 # Return the serializable result
#                 # The MongoJSONEncoder will handle the conversion automatically
#                 # Or use the explicitly converted result
#                 return jsonify(serializable_result), 200
                
#             except Exception as e:
#                 # Clean up in case of error
#                 if os.path.exists(file_path):
#                     os.remove(file_path)
#                 print(f"Error in analyze_resume: {str(e)}")
#                 raise e
#         else:
#             return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
    
#     except Exception as e:
#         print(f"Exception in analyze_resume: {str(e)}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({'status': 'healthy'}), 200

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8502)



from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from bson.json_util import dumps
from flask_cors import CORS, cross_origin

# Import modules
from src.config import config
from src.s3_storage import S3Storage
from src.mongodb_manager import MongoDBManager
from src.pdf_extractor import PDFExtractor
from src.resume_analyzer import ResumeAnalyzer
from src.ats_scorer import ATSScorer

from bson import ObjectId
import json
from json import JSONEncoder





# Initialize Flask app
app = Flask(__name__)

CORS(
    app,
    methods=["GET", "POST"],
    resources={r"/*": {"origins": "*", "send_wildcard": "False"}},
)
app.config["CORS_HEADERS"] = "*"


class MongoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MongoJSONEncoder, self).default(obj)


# Configure upload folder
app.config['UPLOAD_FOLDER'] = config.upload_folder

# Create upload folder if it doesn't exist
os.makedirs(config.upload_folder, exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.allowed_extensions

def convert_objectid_to_str(obj):
    """
    Recursively convert any ObjectId instances in a nested object to strings
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    return obj

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    """
    Endpoint to analyze a resume against a job description
    
    Request should include:
    - resume: PDF file
    - job_description: Text of the job description
    - userid: User ID for metadata
    - name: User name for metadata
    
    Returns:
    - JSON with analysis results, including S3 URL and MongoDB ID
    """
    try:
        # Check if the post request has the file part
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        
        job_description = request.form.get('job_description')
        user_id = request.form.get('userid')
        name = request.form.get('name')
        
        metadata = {"userid": user_id, "name": name}
        
        if not job_description:
            return jsonify({'error': 'No job description provided'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Save the file temporarily
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # Initialize services
                s3_storage = S3Storage()
                mongodb_manager = MongoDBManager()
                pdf_extractor = PDFExtractor()
                resume_analyzer = ResumeAnalyzer()
                ats_scorer = ATSScorer()
                
                # Extract text from PDF
                resume_text = pdf_extractor.extract_text(file_path)
                print("PDF text extracted successfully")
                print("resume_text:",resume_text)
                
                # Save resume text to temporary txt file
                txt_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename.rsplit('.', 1)[0]}.txt")
                with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(resume_text)
                print("Resume text saved to txt file")
                
                # Upload original PDF to S3
                file_url = s3_storage.upload_resume(file_path, metadata)
                
                # Extract resume information using separate prompt
                resume_info = resume_analyzer.get_key_resume_data(resume_text,job_description)
                print("Resume information extracted")
                relevant_years_experience = resume_info["relevant_experience_years"]
                print(relevant_years_experience)
                # print("resume information:",resume_info)
                
                # Calculate ATS score using separate prompt
                ats_analysis = ats_scorer.calculate_score(resume_text, job_description,relevant_years_experience)
                print("ATS analysis completed")
                # print("ats score:",ats_analysis)
                
                ats_analysis.update(resume_info)
                print(ats_analysis)


                
                # Combine all data
                result = {
                    "ats_analysis": ats_analysis,
                    "file_url": file_url,
                    "metadata": metadata,
                    "job_description": job_description
                }
                
                # Save to MongoDB
                mongo_id = mongodb_manager.save_candidate_data(result)
                
                # Add MongoDB ID to result
                result["mongo_id"] = mongo_id
                
                # Convert any ObjectId instances in the result
                serializable_result = convert_objectid_to_str(result)
                mongodb_manager.close_connection()
                
                # Clean up the temporary files
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(txt_file_path):
                    os.remove(txt_file_path)
                print("Temporary files cleaned up")
                
                # Return the serializable result
                return jsonify(serializable_result), 200
                
            except Exception as e:
                # Clean up in case of error
                if os.path.exists(file_path):
                    os.remove(file_path)
                txt_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename.rsplit('.', 1)[0]}.txt")
                if os.path.exists(txt_file_path):
                    os.remove(txt_file_path)
                print(f"Error in analyze_resume: {str(e)}")
                raise e
        else:
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
    
    except Exception as e:
        print(f"Exception in analyze_resume: {str(e)}")
        return jsonify({'error': str(e)}), 500
    


@app.route("/candidate_search", methods=["POST"])
def get_candidate_by_email():


    mongodb_manager = MongoDBManager()
    # Get email parameter from request
    data = request.get_json()
    # print(data)
    email = data["email"]
    
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400
    
    # Query the database for candidate with matching email
    candidate = mongodb_manager.find_candidate_by_email(email)
    print(candidate)
    mongodb_manager.close_connection()
    
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404
    

    
    # Convert ObjectId to string using dumps from bson.json_util
    return dumps(candidate), 200, {"Content-Type": "application/json"}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8502)