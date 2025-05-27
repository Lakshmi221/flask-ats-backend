
import os
import boto3
import uuid
import botocore
from src.config import config

class S3Storage:
    """Class for AWS S3 operations"""
    
    def __init__(self):
        """Initialize S3 client with credentials from config"""
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=config.aws_access_key,
            aws_secret_access_key=config.aws_secret_key,
            region_name=config.s3_region
        )
        self.bucket_name = config.s3_bucket_name
        self.region = config.s3_region
        
        # Ensure the bucket exists - explicitly calling the method here
        self._ensure_bucket_exists()
        
    def _ensure_bucket_exists(self):
        """Check if the bucket exists and create it if it doesn't"""
        try:
            # Check if bucket exists
            self.s3.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} already exists")
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                print(f"Bucket {self.bucket_name} does not exist. Creating...")
                try:
                    if self.region == 'us-east-1':
                        # For us-east-1, the LocationConstraint should be omitted
                        self.s3.create_bucket(Bucket=self.bucket_name)
                    else:
                        # For other regions, specify the LocationConstraint
                        self.s3.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    print(f"Bucket {self.bucket_name} created successfully")
                    
                    # Set bucket to private access by default
                    self.s3.put_public_access_block(
                        Bucket=self.bucket_name,
                        PublicAccessBlockConfiguration={
                            'BlockPublicAcls': True,
                            'IgnorePublicAcls': True,
                            'BlockPublicPolicy': True,
                            'RestrictPublicBuckets': True
                        }
                    )
                    
                    print(f"Privacy settings applied to bucket {self.bucket_name}")
                except Exception as create_error:
                    print(f"Error creating bucket: {str(create_error)}")
                    raise
            elif error_code == '403':
                # Bucket exists but user doesn't have access
                print(f"Access denied to bucket {self.bucket_name}. Please check your AWS credentials and permissions.")
                raise
            else:
                # Some other error
                print(f"Error checking bucket: {str(e)}")
                raise
    
    def upload_resume(self, file_path, metadata=None):
        """
        Upload a resume file to S3 bucket
        
        Args:
            file_path: Path to the file to upload
            metadata: Optional metadata dict to attach to the file
            
        Returns:
            str: URL of the uploaded file
        """
        try:
            # Generate a unique filename to avoid collisions
            file_name = os.path.basename(file_path)
            unique_filename = f"{uuid.uuid4()}-{file_name}"
            
            # Upload file with metadata
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = {k: str(v) for k, v in metadata.items()}
            
            # Upload the file
            self.s3.upload_file(
                file_path, 
                self.bucket_name, 
                unique_filename,
                ExtraArgs=extra_args
            )
            
            # Generate pre-signed URL that expires in 1 hour (3600 seconds)
            # This allows temporary access to the file even with private bucket settings
            file_url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': unique_filename
                },
                ExpiresIn=3600
            )
            
            # Alternatively, if you want a permanent URL (requires proper bucket permissions):
            # file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{unique_filename}"
            
            return file_url
        except Exception as e:
            print(f"Error uploading to S3: {str(e)}")
            raise

    def delete_resume(self, file_url):
        """
        Delete a resume file from S3 bucket using its URL
        
        Args:
            file_url: URL of the file to delete (can be pre-signed URL or regular S3 URL)
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            # Extract the key (filename) from the URL
            # Handle both pre-signed URLs and regular S3 URLs
            if '?' in file_url:
                # Pre-signed URL - extract everything before the query parameters
                base_url = file_url.split('?')[0]
            else:
                base_url = file_url
                
            # Extract the key from the URL
            # URL format: https://bucket-name.s3.amazonaws.com/key (for us-east-1)
            # or https://bucket-name.s3.region.amazonaws.com/key (for other regions)
            if f"{self.bucket_name}.s3.amazonaws.com/" in base_url:
                # Format: https://bucket-name.s3.amazonaws.com/key
                key = base_url.split(f"{self.bucket_name}.s3.amazonaws.com/")[1]
            elif f"{self.bucket_name}.s3.{self.region}.amazonaws.com/" in base_url:
                # Format: https://bucket-name.s3.region.amazonaws.com/key
                key = base_url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/")[1]
            else:
                raise ValueError("Invalid S3 URL format")
            
            # Delete the object from S3
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            print(f"File {key} deleted successfully from S3")
            return True
            
        except Exception as e:
            print(f"Error deleting file from S3: {str(e)}")
            return False