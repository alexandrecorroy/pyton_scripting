from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

import os

load_dotenv()

class MongoDbLogger:
    def __init__(self, uri=os.getenv("MONGODB_URI"), db_name=os.getenv("MONGODB_DATABASE"), collection=os.getenv("MONGODB_COLLECTION")):
        self.client = MongoClient(uri)
        self.db = self.client.get_database(db_name)
        self.collection = self.db.get_collection(collection)
    

    def log(self, level, message):
        document = {
            "timestamp": datetime.now(),
            "level": level,
            "message": message,
        }
        document = {k:v for k,v in document.items() if v is not None }
        self.collection.insert_one(document)
