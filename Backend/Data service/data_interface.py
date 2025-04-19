from abc import ABC, abstractmethod
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Tuple
from bson.objectid import ObjectId

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
            filter = {"_id": ObjectId(record_id)}
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
        except ValueError as e:
            return "", Exception(f"Invalid record ID: {e}")
        
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
    

    def close(self):
        self.client.close()


def main():
    # format (figure in Slack):
    # "data": {
    #             "address": "456 New St",
    #             "latitude": 21.0285,
    #             "longitude": 105.8542,
    #             "category": "cultural",
    #             "name": "Hanoi Old Quarter"
    #         }


    # Initialize the MongoDB connection
    try:
        db = MongoDB("mongodb://127.0.0.1:27017", "travel_db", "locations")
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