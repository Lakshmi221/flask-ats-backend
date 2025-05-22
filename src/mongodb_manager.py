from pymongo import MongoClient
from src.config import config

class MongoDBManager:
    """Class for MongoDB operations"""
    
    def __init__(self):
        """Initialize MongoDB client with credentials from config"""
        self.client = MongoClient(config.mongo_uri)
        self.db = self.client[config.mongo_db_name]
        self.collection = self.db[config.mongo_collection]
    
    def save_candidate_data(self, data):
        """
        Save candidate data to MongoDB
        
        Args:
            data: Dictionary containing candidate data to save
            
        Returns:
            str: ID of the inserted document
        """
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving to MongoDB: {str(e)}")
            raise
    
    def find_candidate_by_email(self, email_id):
        """
        Find a candidate by ID
        
        Args:
            candidate_id: ID of the candidate to find
            
        Returns:
            dict: Candidate data or None if not found
        """
        try:
            # return self.collection.find_one({"_id": candemailidate_id})
            candidate = self.collection.find_one({"ats_analysis.Email": email_id})
            return candidate
        except Exception as e:
            print(f"Error finding candidate in MongoDB: {str(e)}")
            raise

    def close_connection(self):
        self.client.close()