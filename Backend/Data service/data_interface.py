from abc import ABC, abstractmethod
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Tuple

class IDatabase(ABC):
    @abstractmethod
    def save_record(self, record: Dict[str, Any]) -> Tuple[str, Exception]:
        pass

    @abstractmethod
    def update_record(self, record: Dict[str, Any]) -> Tuple[str, Exception]:
        pass

    @abstractmethod
    def find_records(self, record_type: str, filter: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Exception]:
        pass


class MongoDB(IDatabase):
    def __init__(self, uri: str, database: str, collection: str):
        self.client = MongoClient(uri)
        try:
            self.client.admin.command('ping')
        except PyMongoError as e:
            raise Exception(f"Failed to connect to MonoDB: {e}")
        self.db = self.client[database]
        self.collection = self.db[collection]

    def save_record(self, record: Dict[str, Any]) -> Tuple[str, Exception]:
        try:
            if not record.get('type'):
                return "", Exception("Record type is required")
            now = int(datetime.now().timestamp())
            record["created_at"] = now 
            record["updated_at"] = now
            result = self.collection.insert_one(record)
            return str(result.inserted_id), None
        except PyMongoError as e:
            return "", Exception(f"failed to save record: {e}")
        
    def update_record(self, record: Dict[str, Any]) -> Tuple[str, Exception]:
        try:
            record_id = record.get("_id")
            if not record_id:
                return "", Exception("Record ID is required for update")
            record["updated_at"] = int(datetime.now().timestamp())
            filter = {"_id": record_id}
            update = {
                "$set": {
                    "data": record.get("data", {}),
                    "type": record.get("type"),
                    "updated_at": record["updated_at"]
                }
            }
            result = self.collection.update_one(filter, update)
            if result.matched_count == 0:
                return "", Exception("No record found with given ID")
            return record_id, None
        except PyMongoError as e:
            return "", Exception(f"Faield to update record: {e}")
        
    def find_records(self, record_type: str, filter: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Exception]:
        try:
            query = {"type": record_type}
            query.update(filter)
            records = list(self.collection.find(query))
            return records, None
        except PyMongoError as e:
            return [], Exception(f"Failed to find records: {e}")
    

    def close(self):
        self.client.close()