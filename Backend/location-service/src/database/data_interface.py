from abc import ABC, abstractmethod
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Tuple
from bson.objectid import ObjectId
from typing import Optional
import os
from bson import json_util
from dotenv import load_dotenv

load_dotenv()

class IDatabase(ABC):
    @abstractmethod
    def save_record(self, record: Dict[str, Any]) -> Tuple[str, Exception]:
        """
        Save a record to the database.
        Args:
            record (Dict[str, Any]): The record to save, in dictionary format.
        Returns:
            Tuple[str, Exception]: A tuple containing the ID of the saved record (if successful) and an error (if any).
        """
        pass

    @abstractmethod
    def update_record(self, record: Dict[str, Any]) -> Tuple[str, Exception]:
        """
        Update a record in the database.
        Args:
            record (Dict[str, Any]): The record to update, must contain "_id" to identify the record.
        Returns:
            Tuple[str, Exception]: A tuple containing the ID of the updated record (if successful) and an error (if any).
        """
        pass

    @abstractmethod
    def find_records(self, record_type: str, filter: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Exception]:
        """
        Find records in the database based on the record type and filter.
        Args:
            record_type (str): The type of record to find (e.g., "location").
            filter (Dict[str, Any]): The filter for the search (e.g., {"data.category": "cultural"}).
        Returns:
            Tuple[List[Dict[str, Any]], Exception]: A tuple containing the list of found records and an error (if any).
        """
        pass


class MongoDB(IDatabase):
    def __init__(self, uri: str, database: str, collection: str):
        try:
            self.client = MongoClient(uri)
            self.client.admin.command('ping')
            print("Successfully connected")
        except PyMongoError as e:
            raise Exception(f"Failed to connect to MonoDB: {str(e)}")
        self.db = self.client[database]
        self.collection = self.db[collection]

    # Add the method to list collection names
    def list_collections(self):
        try:
            return self.db.list_collection_names()  # Call on the database object
        except PyMongoError as e:
            return [], Exception(f"failed to list collections: {str(e)}")
        
    def save_record(self, record: Dict[str, Any]):
        try:
            if not record.get('type'):
                return "", Exception("Record type is required")
            now = int(datetime.now().timestamp())
            record["created_at"] = now 
            record["updated_at"] = now
            result = self.collection.insert_one(record)
            return result
        except PyMongoError as e:
            return "", Exception(f"failed to save record: {e}")


    def update_record(self, record: Dict[str, Any]) -> Tuple[str, Exception]:
        try:
            record_id = record.get("_id")
            if not record_id:
                return "", Exception("Record ID is required for update")
            
            # Đảm bảo record_id là ObjectId
            try:
                record_id = ObjectId(record_id)
            except (ValueError, TypeError):
                return "", Exception("Invalid record ID format")

            record["updated_at"] = int(datetime.now().timestamp())
            filter = {"_id": record_id}

            # Lấy các trường từ record để cập nhật
            update = {
                "$set": {
                    "data": record.get("data", {}),
                    "type": record.get("type"),
                    "location": record.get("location"),  # Thêm trường location
                    "updated_at": record["updated_at"]
                }
            }

            # Thực hiện cập nhật
            result = self.collection.update_one(filter, update)
            if result.matched_count == 0:
                return "", Exception("No record found with given ID")
            
            return str(record_id), None  # Trả về record_id dưới dạng string

        except PyMongoError as e:
            return "", Exception(f"Failed to update record: {e}")
        except ValueError as e:
            return "", Exception(f"Invalid record ID: {e}")
        except Exception as e:
            return "", Exception(f"Unexpected error during update: {e}")
      
        
    def find_records(self, record_type: str, filter: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Exception]:
        try:
            query = {"type": record_type}
            if "_id" in filter:
                filter["_id"] = ObjectId(filter["_id"])
            query.update(filter)
            records = list(self.collection.find(query))
            return records, None
        except PyMongoError as e:
            return [], Exception(f"Failed to find records: {e}")
        except ValueError as e:
            return [], Exception(f"Invalid filter value: {e}")
    
    def find_one(self, query):
        return self.collection.find_one(query)
    def find(self, query: dict = {}, projection: Optional[dict] = None, limit: Optional[int] = None) -> List[dict]:
        """
        Truy vấn nhiều document trong collection.

        Args:
            query (dict): Điều kiện lọc MongoDB.
            projection (dict, optional): Chỉ định các trường cần lấy.
            limit (int, optional): Giới hạn số lượng kết quả.

        Returns:
            List[dict]: Danh sách các document phù hợp.
        """
        cursor = self.collection.find(query, projection)
        if limit:
            cursor = cursor.limit(limit)
        result = list(cursor)
        return [json_util.loads(json_util.dumps(doc)) for doc in result]
    def update_one(self, query, update):
        return self.collection.update_one(query, update)
    def count_documents(self, filter=None):
        if filter is None:
            filter = {}
        return self.collection.count_documents(filter)

    def close(self):
        self.client.close()


def main():
    # Initialize the MongoDB connection
    try:
        DB_URL = os.environ.get('TRAVELDB_URL')
        db = MongoDB(DB_URL, "travel_db", "locations")
    except Exception as e:
        print(f"Error initializing MongoDB: {e}")
        return

    # Save a new record
    new_location = {
        "type": "location",
        "data": {
            "address": "123 Main St",
            "latitude": 21.0285,
            "longitude": 105.8542,
            "category": "cultural",
            "name": "Hanoi Old Quarter"
        }
    }
    record_id, error = db.save_record(new_location)
    if error:
        print(f"Error saving record: {error}")
    else:
        print(f"Successfully saved record with ID: {record_id}")

    # Find records (e.q., find all locations with category "cultural")
    filter = {"data.category": "cultural"}
    records, error = db.find_records("location", filter)
    if error:
        print(f"Error finding records: {error}")
    else:
        print("Found records:")
        for record in records:
            print(f"- ID: {record['_id']}, Name: {record['data']['name']}, Category: {record['data']['category']}")

    # Update an existing record
    if record_id:
        updated_location = {
            "_id": record_id,
            "type": "location",
            "data": {
                "address": "456 New St [updated]",
                "latitude": 21.0285,
                "longitude": 105.8542,
                "category": "cultural",
                "name": "Hanoi Old Quarter"
            }
        }
        updated_id, error = db.update_record(updated_location)
        if error:
            print(f"Error updating record: {error}")
        else:
            print(f"Successfully updated record with ID: {updated_id}")

        # Verify
        records, error = db.find_records("location", {"_id": record_id})
        if error:
            print(f"Error finding updated record: {error}")
        else:
            print("Updated record (ID [ORI] - Data [NEW]):")
            for record in records:
                print(f"- ID: {record['_id']}, Name: {record['data']['name']}, Category: {record['data']['category']}")

    db.close()
    print("MongoDB connection closed.")


if __name__ == "__main__":
    main()