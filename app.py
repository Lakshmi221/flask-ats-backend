from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from bson.json_util import dumps
from flask_cors import CORS, cross_origin
import concurrent.futures
import threading
from typing import List, Dict, Any
import uuid
import time

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

# Thread-local storage for database connections
thread_local = threading.local()

def get_services():
    """Get thread-local instances of services"""
    if not hasattr(thread_local, 'services'):
        thread_local.services = {
            's3_storage': S3Storage(),
            'mongodb_manager': MongoDBManager(),
            'pdf_extractor': PDFExtractor(),
            'resume_analyzer': ResumeAnalyzer(),
            'ats_scorer': ATSScorer()
        }
    return thread_local.services

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

def process_single_resume(file_data: Dict[str, Any], job_description: str, 
                         user_id: str, name: str, batch_id: str) -> Dict[str, Any]:
    """
    Process a single resume file
    
    Args:
        file_data: Dictionary containing file info and content
        job_description: Job description text
        user_id: User ID for metadata
        name: User name for metadata
        batch_id: Unique batch identifier
        
    Returns:
        Dictionary with processing results
    """
    result = {
        'filename': file_data['filename'],
        'status': 'success',
        'error': None,
        'data': None
    }
    
    file_path = None
    txt_file_path = None
    
    try:
        # Get thread-local services
        services = get_services()
        
        # Create unique filename to avoid conflicts
        unique_filename = f"{batch_id}_{file_data['filename']}"
        filename = secure_filename(unique_filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file temporarily
        with open(file_path, 'wb') as f:
            f.write(file_data['content'])
        
        metadata = {
            "userid": user_id, 
            "name": name,
            "batch_id": batch_id,
            "original_filename": file_data['filename']
        }
        
        # Extract text from PDF
        resume_text = services['pdf_extractor'].extract_text(file_path)
        print(f"PDF text extracted successfully for {file_data['filename']}")
        
        # Save resume text to temporary txt file
        txt_filename = f"{filename.rsplit('.', 1)[0]}.txt"
        txt_file_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(resume_text)
        
        # Upload original PDF to S3
        file_url = services['s3_storage'].upload_resume(file_path, metadata)
        
        # Extract resume information
        resume_info = services['resume_analyzer'].get_key_resume_data(resume_text, job_description)
        print(f"Resume information extracted for {file_data['filename']}")
        
        relevant_years_experience = resume_info.get("relevant_experience_years", 0)
        
        # Calculate ATS score
        ats_analysis = services['ats_scorer'].calculate_score(resume_text, job_description, relevant_years_experience)
        print(f"ATS analysis completed for {file_data['filename']}")
        
        # Combine all data
        ats_analysis.update(resume_info)
        
        analysis_result = {
            "ats_analysis": ats_analysis,
            "file_url": file_url,
            "metadata": metadata,
            "job_description": job_description,
            "processing_timestamp": time.time()
        }
        
        # Save to MongoDB
        services['mongodb_manager'].save_candidate_data(analysis_result)
        
        result['data'] = {
            'file_url': file_url,
            'ats_score': ats_analysis.get('overall_match_percentage', 0),
            'candidate_name': ats_analysis.get('candidate_name', 'unknown'),
            'email': ats_analysis.get('Email', 'unknown'),
            'experience_years': ats_analysis.get('total_experience_years', 0)
        }
        
        print(f"Successfully processed {file_data['filename']}")
        
    except Exception as e:
        print(f"Error processing {file_data['filename']}: {str(e)}")
        result['status'] = 'error'
        result['error'] = str(e)
    
    finally:
        # Clean up temporary files
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        if txt_file_path and os.path.exists(txt_file_path):
            try:
                os.remove(txt_file_path)
            except:
                pass
    
    return result

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    """
    Endpoint to analyze single resume (backwards compatibility)
    """
    try:
        # Check if the post request has the file part
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        job_description = request.form.get('job_description')
        user_id = request.form.get('userid')
        name = request.form.get('name')
        
        if not job_description:
            return jsonify({'error': 'No job description provided'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not (file and allowed_file(file.filename)):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
        
        # Convert single file to batch format
        batch_id = str(uuid.uuid4())
        file_data = {
            'filename': file.filename,
            'content': file.read()
        }
        
        # Process single file
        result = process_single_resume(file_data, job_description, user_id, name, batch_id)
        
        if result['status'] == 'error':
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'message': 'Resume analyzed successfully',
            'data': result['data']
        }), 201
        
    except Exception as e:
        print(f"Exception in analyze_resume: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_resumes_batch', methods=['POST'])
def analyze_resumes_batch():
    """
    Endpoint to analyze multiple resumes in parallel
    
    Request should include:
    - resumes: Multiple PDF files
    - job_description: Text of the job description
    - userid: User ID for metadata
    - name: User name for metadata
    - max_workers: Optional, maximum number of parallel workers (default: 4)
    
    Returns:
    - JSON with batch analysis results
    """
    try:
        # Check if files are provided
        if 'resumes' not in request.files:
            return jsonify({'error': 'No resume files provided'}), 400
        
        files = request.files.getlist('resumes')
        job_description = request.form.get('job_description')
        user_id = request.form.get('userid')
        name = request.form.get('name')
        max_workers = int(request.form.get('max_workers', 4))
        
        # Validate inputs
        if not job_description:
            return jsonify({'error': 'No job description provided'}), 400
        
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        
        # Validate file types and prepare file data
        file_data_list = []
        invalid_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if not allowed_file(file.filename):
                invalid_files.append(file.filename)
                continue
            
            file_data_list.append({
                'filename': file.filename,
                'content': file.read()
            })
        
        if invalid_files:
            return jsonify({
                'error': f'Invalid file types found: {", ".join(invalid_files)}. Only PDF files are allowed'
            }), 400
        
        if not file_data_list:
            return jsonify({'error': 'No valid PDF files found'}), 400
        
        # Generate unique batch ID
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        
        print(f"Starting batch processing of {len(file_data_list)} resumes with {max_workers} workers")
        
        # Process files in parallel
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_filename = {
                executor.submit(
                    process_single_resume, 
                    file_data, 
                    job_description, 
                    user_id, 
                    name, 
                    batch_id
                ): file_data['filename'] 
                for file_data in file_data_list
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_filename):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    filename = future_to_filename[future]
                    print(f"Error processing {filename}: {str(e)}")
                    results.append({
                        'filename': filename,
                        'status': 'error',
                        'error': str(e),
                        'data': None
                    })
        
        processing_time = time.time() - start_time
        
        # Compile summary
        successful_results = [r for r in results if r['status'] == 'success']
        failed_results = [r for r in results if r['status'] == 'error']
        
        summary = {
            'batch_id': batch_id,
            'total_files': len(file_data_list),
            'successful': len(successful_results),
            'failed': len(failed_results),
            'processing_time_seconds': round(processing_time, 2),
            'results': results
        }
        
        print(f"Batch processing completed: {len(successful_results)}/{len(file_data_list)} successful")
        
        # Close any remaining database connections
        try:
            if hasattr(thread_local, 'services'):
                thread_local.services['mongodb_manager'].close_connection()
        except:
            pass
        
        return jsonify({
            'message': f'Batch processing completed. {len(successful_results)} out of {len(file_data_list)} resumes processed successfully.',
            'summary': summary
        }), 201
        
    except Exception as e:
        print(f"Exception in analyze_resumes_batch: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/candidate_search", methods=["POST"])
def get_candidate_by_email():
    mongodb_manager = MongoDBManager()
    # Get email parameter from request
    data = request.get_json()
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



@app.route("/candidate_delete", methods=["DELETE"])
def delete_candidate_by_id():
    mongodb_manager = MongoDBManager()
    s3_storage = S3Storage()
    
    # Get candidate_id parameter from request
    data = request.get_json()
    candidate_id = data.get("candidate_id")
    
    if not candidate_id:
        mongodb_manager.close_connection()
        return jsonify({"error": "candidate_id parameter is required"}), 400
    
    try:
        # First, get the candidate to retrieve the file_url before deletion
        candidate = mongodb_manager.find_candidate_by_id(candidate_id)
        
        if not candidate:
            mongodb_manager.close_connection()
            return jsonify({"error": "Candidate not found"}), 404
        
        # Extract file_url from candidate document
        file_url = candidate.get("file_url")
        
        # Delete the candidate from database
        result = mongodb_manager.delete_candidate_by_id(candidate_id)
        
        if result["success"]:
            # If database deletion successful, also delete from S3
            s3_delete_success = True
            if file_url:
                try:
                    s3_delete_success = s3_storage.delete_resume(file_url)
                    if not s3_delete_success:
                        print(f"Warning: Failed to delete file from S3: {file_url}")
                except Exception as s3_error:
                    print(f"Error deleting file from S3: {str(s3_error)}")
                    s3_delete_success = False
            
            mongodb_manager.close_connection()
            
            # Return success response with additional info about S3 deletion
            response_message = result["message"]
            if file_url:
                if s3_delete_success:
                    response_message += " and associated file deleted from storage"
                else:
                    response_message += " but failed to delete associated file from storage"
            
            return jsonify({
                "message": response_message,
                "deleted_count": result["deleted_count"],
                "s3_deletion_success": s3_delete_success if file_url else None
            }), 200
        else:
            mongodb_manager.close_connection()
            return jsonify({"error": result["message"]}), 404
            
    except Exception as e:
        mongodb_manager.close_connection()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/candidates_summary", methods=["GET"])
def get_candidates_summary():
    """
    Get candidates summary with essential fields only (for better performance)
    """
    mongodb_manager = MongoDBManager()
    
    try:
        # Get candidates summary (only essential fields)
        candidates = mongodb_manager.get_candidates_summary_list()
        mongodb_manager.close_connection()
        
        if not candidates:
            return jsonify({"error": "No candidates found"}), 404
        
        response_data = {
            "candidates": candidates,
            "total_returned": len(candidates),
            "note": "This endpoint returns only essential fields for better performance"
        }
        
        # Convert ObjectId to string using dumps from bson.json_util
        return dumps(response_data), 200, {"Content-Type": "application/json"}
        
    except Exception as e:
        mongodb_manager.close_connection()
        print(f"Error in get_candidates_summary: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8502)