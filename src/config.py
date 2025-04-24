# import os
# from dotenv import load_dotenv

# class Config:
#     """Configuration manager for the application"""
    
#     def __init__(self):
#         # Load environment variables
#         load_dotenv()
        
#         # OpenAI configuration
#         self.openai_api_key = self._get_env_var("OPENAI_API_KEY")
        
#         # AWS S3 configuration
#         self.aws_access_key = self._get_env_var("AWS_ACCESS_KEY")
#         self.aws_secret_key = self._get_env_var("AWS_SECRET_KEY")
#         self.s3_bucket_name = self._get_env_var("S3_BUCKET_NAME")
#         self.s3_region = os.getenv("S3_REGION", "us-east-1")
        
#         # MongoDB configuration
#         self.mongo_uri = self._get_env_var("MONGO_URI")
#         self.mongo_db_name = os.getenv("MONGO_DB_NAME", "resume_analyzer")
#         self.mongo_collection = os.getenv("MONGO_COLLECTION", "candidates")
        
#         # WhatsApp configuration
#         self.account_sid = os.getenv("ACCOUNT_SID")
#         self.auth_token = os.getenv("AUTH_TOKEN")
        
#         # Flask configuration
#         self.upload_folder = 'temp_uploads'
#         self.allowed_extensions = {'pdf'}
        
#     def _get_env_var(self, var_name):
#         """Get environment variable or raise error if not found"""
#         value = os.getenv(var_name)
#         if not value:
#             raise ValueError(f"{var_name} environment variable is not set.")
#         return value

# # Create singleton instance
# config = Config()




import os
from dotenv import load_dotenv

class Config:
    """Configuration manager for the application"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # OpenAI configuration
        self.openai_api_key = self._get_env_var("OPENAI_API_KEY")
        
        # AWS S3 configuration
        self.aws_access_key = self._get_env_var("AWS_ACCESS_KEY")
        self.aws_secret_key = self._get_env_var("AWS_SECRET_KEY")
        self.s3_bucket_name = self._get_env_var("S3_BUCKET_NAME")
        self.s3_region = os.getenv("S3_REGION", "us-east-1")
        self.create_bucket_if_not_exists = os.getenv("CREATE_BUCKET_IF_NOT_EXISTS", "true").lower() == "true"
        
        # MongoDB configuration
        self.mongo_uri = self._get_env_var("MONGO_URI")
        self.mongo_db_name = os.getenv("MONGO_DB_NAME", "resume_analyzer")
        self.mongo_collection = os.getenv("MONGO_COLLECTION", "candidates")
        
        # WhatsApp configuration
        self.account_sid = os.getenv("ACCOUNT_SID")
        self.auth_token = os.getenv("AUTH_TOKEN")
        
        # Flask configuration
        self.upload_folder = 'temp_uploads'
        self.allowed_extensions = {'pdf'}
        
    def _get_env_var(self, var_name):
        """Get environment variable or raise error if not found"""
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"{var_name} environment variable is not set.")
        return value

# Create singleton instance
config = Config()