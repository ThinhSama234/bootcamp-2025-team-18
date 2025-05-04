import uuid
import re
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../agent")))
from graph import Graph

class SuggestionService:
  def __init__(self, messages: list[str], faiss_name: str = None):
    self.messages = messages
    # Chạy graph.py để lấy location_details và response
    graph = Graph(faiss_name=faiss_name)
    self.location_details, self.response = graph.process_messages(messages)
    
  def get_session_id(self) -> str:
    return str(uuid.uuid4())

  def get_location_ids(self, k: int) -> list[str]: # done
    # This is a placeholder implementation. In a real-world scenario, this would involve
    # complex logic to determine the location IDs based on the messages.
    return [str(loc["_id"]) for loc in self.location_details[:k]]
  
  def get_location_description(self, location_id: str) -> str: #???
    # This is a placeholder implementation. In a real-world scenario, this would involve
    # complex logic to determine the location description based on the location ID.
    return f"Description for location {location_id}"
  

if __name__ == "__main__":
    messages = ["Tôi nghĩ chúng ta nên đi đến một nơi có đồi núi."]
    suggestion_service = SuggestionService(messages, faiss_name="v20250504_161455")
    location_ids = suggestion_service.get_location_ids(k=5)
    print("Location IDs:", location_ids)
