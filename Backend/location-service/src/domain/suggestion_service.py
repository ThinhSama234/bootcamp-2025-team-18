from typing import List
import os
import uuid
import logging
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from bson.objectid import ObjectId
from agent.graph import Graph
from agent.format import TextProcessor
from database.data_interface import MongoDB
logger = logging.getLogger(__name__)

from config.config import TRAVELDB_URL

class SuggestionService:
  def __init__(self, db: MongoDB, db_vector: MongoDB):
    self.graph = Graph(db, db_vector)
    self.db = db
    self.db_vector = db_vector
    self.text_processor = TextProcessor()
    
  def get_session_id(self) -> str:
    return str(uuid.uuid4())

  def get_location_ids(self, k: int, messages: list[str], image_urls: list[str] = None, coordinates: any = None) -> list[str]: # done
    initial_state = {"messages": messages}
    state = self.graph.summarize(initial_state)
    state = self.graph.search_vector_db(self.db_vector, state, k)
    location_details = state["location_details"]
    logger.info(location_details)
    
    return location_details
  # query k list id mongo
  
  def get_location_details_by_id(self, location_id: str) -> dict:
    try:   
      record = self.db.find_one({"_id":ObjectId(str(location_id))})
      if not record:
        return {"error": f"No document found for location_id {location_id}"}
      logger.info(f"Record for ID {location_id}: {record}")
      data = record.get('data', {})
      return {
        "_id": str(record.get("_id")),
        "type": record.get('type'),
        "name": data.get('name', ''),
        "category": data.get('category', '').lower(),
        "address": data.get('address', ''),
        "description": data.get('description', ''),
        "image_url": data.get('image_url', '')
      }
    except Exception as e:
      return {"error": f"Error fetching data for location_id {location_id}: {str(e)}"}

  def get_location_response(self, messages: List[str], location_id: str) -> str:
    """
    Tạm thời bây giờ, câu response sẽ là câu mô tả
    """
    try:
      details = self.get_location_details_by_id(location_id)
      # Kiểm tra nếu có lỗi
      if "error" in details:
        return details["error"]
      record = {
        "_id": details.get("_id"),
        "data": {
          "name": details.get("name", "Địa điểm"),
          "address": details.get("address", "Địa chỉ không rõ"),
          "description": details.get("description", "Mô tả không có"),
          "category": details.get("category", "Không rõ danh mục")
        }
      }

      response = self.text_processor.format_response(messages, record)
      return response
      
    except Exception as e:
      return f"Error fetching description for location_id {location_id}: {str(e)}"





if __name__ == "__main__":
  messages = [
    "Tôi nghĩ chúng ta nên đi đến Ninh Bình.",
    "Ồ, đó thực sự là danh lam thắng cảnh nổi tiếng.",
    "Tuyệt vời, tôi cũng đang muốn ăn món núi rừng"
  ]
  # messages = [
  #   "Mọi người ơi, cuối tuần này chúng ta đi leo thác không nhỉ",
  #   "Ồ, tôi cũng đang muốn chill.",
  #   "Hay là đi Đà Lạt nhỉ, thời tiết se lạnh leo thác cho đỡ mệt"
  # ]
  # messages = [
  #   "Tôi muốn đi leo núi"
  # ]
  uri = TRAVELDB_URL
  db = MongoDB(uri, database="travel_db", collection="location_plus")
  db_vector = MongoDB(uri, database="travel_db", collection="locations_vector_plus")
  suggestion_service = SuggestionService(db, db_vector)
  location_ids = suggestion_service.get_location_ids(k=20, messages=messages)
  logger.info("Location IDs:", location_ids)

  for sample_id in location_ids:
    details = suggestion_service.get_location_details_by_id(sample_id)
    logger.info("\nInformation for ID", sample_id)
    logger.info("Location address", details["address"])
    logger.info("Location name", details["name"])


  for sample_id in location_ids:
    location_response = suggestion_service.get_location_response(messages, sample_id)
    logger.info("\nLocation Response for ID", sample_id, ":", location_response)
