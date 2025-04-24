from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

# Import modules
from src.config import config
from src.s3_storage import S3Storage
from src.mongodb_manager import MongoDBManager
from src.pdf_extractor import PDFExtractor
from src.resume_analyzer import ResumeAnalyzer
from src.ats_scorer import ATSScorer

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = config.upload_folder

# Create upload folder if it doesn't exist
os.makedirs(config.upload_folder, exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.allowed_extensions

@app.route('/analyze-resume', methods=['POST'])
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
                
                # Upload to S3
                file_url = s3_storage.upload_resume(file_path, metadata)
                # print(f"Resume uploaded to S3: {file_url}")
                
                # Extract resume information
                resume_info = resume_analyzer.extract_information(resume_text)
                print("Resume information extracted")
                
                # Calculate ATS score
                ats_analysis = ats_scorer.calculate_score(resume_text, job_description)
                print("ATS analysis completed")
                
                # Combine all data
                result = {
                    "resume_info": resume_info,
                    "ats_analysis": ats_analysis,
                    "file_url": file_url,
                    "metadata": metadata,
                    "job_description": job_description
                }
                
                # Save to MongoDB
                mongo_id = mongodb_manager.save_candidate_data(result)
                result["mongo_id"] = mongo_id
                print(f"Data saved to MongoDB with ID: {mongo_id}")
                
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                return jsonify(result), 200
                
            except Exception as e:
                # Clean up in case of error
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
        else:
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8502)