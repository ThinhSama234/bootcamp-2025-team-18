from abc import ABC, abstractmethod
from datetime import datetime
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Tuple
from bson.objectid import ObjectId

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
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
            self.client = AsyncIOMotorClient(uri)
            self.client.admin.command('ping')
            print("Successfully connected")
        except PyMongoError as e:
            raise Exception(f"Failed to connect to MonoDB: {e}")
        self.db = self.client[database]
        self.collection = self.db[collection]

    async def save_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        now = int(datetime.now().timestamp())
        if "created_at" not in record:
            record["created_at"] = now
        if "updated_at" not in record:
            record["updated_at"] = now
        result = await self.collection.insert_one(record)
        record["_id"] = result.inserted_id
        return record
    async def count_documents(self, filter: None) -> int:
        """Đếm số lượng tài liệu theo query."""
        return await self.collection.count_documents(filter)

    async def insert_many(self, documents: list, ordered: bool = False):
        """Chèn nhiều tài liệu vào collection."""
        return await self.collection.insert_many(documents, ordered=ordered)

    def close(self):
        """Đóng kết nối."""
        self.client.close()
    async def update_record(self, record: Dict[str, Any]) -> str:
        """Cập nhật một tài liệu trong collection và trả về ID của tài liệu."""
        try:
            record_id = record.get("_id")
            if not record_id:
                raise Exception("Record ID is required for update")
            
            record["updated_at"] = int(datetime.now().timestamp())
            filter = {"_id": ObjectId(record_id)}
            update = {
                "$set": {
                    "data": record.get("data", {}),
                    "type": record.get("type"),
                    "updated_at": record["updated_at"]
                }
            }
            result = await self.collection.update_one(filter, update)
            if result.matched_count == 0:
                raise Exception("No record found with given ID")
            return str(record_id)
        except PyMongoError as e:
            raise Exception(f"Failed to update record: {e}")
        except ValueError as e:
            raise Exception(f"Invalid record ID: {e}")

    async def find_records(self, record_type: str, filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Tìm kiếm các tài liệu theo loại và bộ lọc."""
        try:
            query = {"type": record_type}
            if "_id" in filter:
                filter["_id"] = ObjectId(filter["_id"])
            query.update(filter)
            records = await self.collection.find(query).to_list(None)
            return records
        except PyMongoError as e:
            raise Exception(f"Failed to find records: {e}")
        except ValueError as e:
            raise Exception(f"Invalid filter value: {e}")

