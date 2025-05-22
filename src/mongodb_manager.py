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
            self.collection.insert_one(data)
            print("candidates data saved successfully")
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
    

 
    def get_candidates_summary_list(self):
        """
        Get all candidates with only essential fields for better performance
        
        Returns:
            list: List of candidate summaries (JSON objects with essential fields only)
        """
        try:
            # Define projection to include only essential fields
            projection = {
                "_id": 1,
                "ats_analysis.candidate_name": 1,
                "ats_analysis.Email": 1,
                "ats_analysis.Phone": 1,
                "ats_analysis.overall_match_percentage": 1,
                "ats_analysis.skills_match_percentage": 1,
                "ats_analysis.experience_match_percentage": 1,
                "ats_analysis.education_match_percentage": 1,
                "ats_analysis.total_experience_years": 1,
                "ats_analysis.relevant_experience_years": 1,
                "ats_analysis.matched_skills": 1,
                "ats_analysis.missing_skills": 1,
                "ats_analysis.highest_education": 1,
                "file_url": 1,
                "metadata": 1
            }
            
            # Find all candidates with projection, sorted by match percentage
            candidates = list(
                self.collection.find({}, projection)
                .sort("ats_analysis.overall_match_percentage", -1)
            )
            
            print(f"Retrieved {len(candidates)} candidate summaries")
            return candidates
            
        except Exception as e:
            print(f"Error retrieving candidate summaries from MongoDB: {str(e)}")
            raise

 


    def close_connection(self):
        self.client.close()

