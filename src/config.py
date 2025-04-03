# Parking spot dimensions
WIDTH = 103
HEIGHT = 43

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "parking_system"
SPOTS_COLLECTION = "parking_spots"
MONITORING_COLLECTION = "monitoring_data"

# Camera/video sources
CAMERA_SOURCES = [
    "data/parking1.mp4",
    "data/parking2.mp4",
    "data/parking3.mp4",
    "data/parking4.mp4",
]

# Threshold for detecting occupied spots
OCCUPANCY_THRESHOLD = 900