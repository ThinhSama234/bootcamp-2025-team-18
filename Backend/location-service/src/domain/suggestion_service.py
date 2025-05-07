import uuid
from agent.graph import Graph
class SuggestionService:
  def __init__(self, faiss_name: str = None):
    self.graph = Graph(faiss_name)
    
  def get_session_id(self) -> str:
    return str(uuid.uuid4())

  def get_location_ids(self, k: int) -> list[str]: # done
    self.location_details, self.response = self.graph.process_messages(messages)
    return [str(loc["_id"]) for loc in self.location_details[:k]]

  def get_location_description(self, location_id: str) -> str:
    for item in self.response:
      if isinstance(item, dict) and "_id" in item and item["_id"] == location_id:
        description = item.get("description", "")
        if description:
          return f"{description}"
        return f"Đây là địa điểm phù hợp với yêu cầu của bạn."
    return f"Đây là địa điểm phù hợp với yêu cầu của bạn."
  

if __name__ == "__main__":
  messages = [
    "Tôi nghĩ chúng ta nên đi đến Ninh Bình.",
    "Tuyệt vời, tôi cũng đang muốn ăn món núi rừng"
  ]
  #suggestion_service = SuggestionService(messages, faiss_name="v20250504_161455")
  suggestion_service = SuggestionService(messages, faiss_name="v20250506_153250")
  location_ids = suggestion_service.get_location_ids(k=5)
  print("Location IDs:", location_ids)
  print("\nAll Location Descriptions:")
  for loc_id in location_ids:
    description = suggestion_service.get_location_description(loc_id)
    print("Description:", description)
