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