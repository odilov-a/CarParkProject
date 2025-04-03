from pymongo import MongoClient
import datetime
from src.config import MONGO_URI, DB_NAME, SPOTS_COLLECTION, MONITORING_COLLECTION

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.spots_collection = self.db[SPOTS_COLLECTION]
        self.monitoring_collection = self.db[MONITORING_COLLECTION]

    def load_positions(self):
        """Load parking spot positions from MongoDB."""
        spots = self.spots_collection.find_one({"_id": "parking_spots"})
        return spots["positions"] if spots else []

    def save_positions(self, pos_list):
        """Save parking spot positions to MongoDB."""
        self.spots_collection.update_one(
            {"_id": "parking_spots"},
            {"$set": {"positions": pos_list}},
            upsert=True
        )

    def log_monitoring_data(self, camera_id, spaces, total_spots):
        """Log monitoring data to MongoDB."""
        self.monitoring_collection.insert_one({
            "camera_id": camera_id,
            "timestamp": datetime.datetime.now(),
            "free_spaces": spaces,
            "total_spaces": total_spots
        })

    def get_monitoring_data(self):
        """Retrieve all monitoring data for analysis."""
        return list(self.monitoring_collection.find())