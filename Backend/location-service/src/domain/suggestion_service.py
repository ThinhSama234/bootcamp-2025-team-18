import uuid
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../agent")))
from extract_metadata import fetch_from_mongodb
from graph import Graph

class SuggestionService:
  def __init__(self, faiss_name: str = None):
    self.graph = Graph(faiss_name)
    
  def get_session_id(self) -> str:
    return str(uuid.uuid4())

  def get_location_ids(self, k: int, messages: list[str], image_urls: list[str]) -> list[str]: # done
    initial_state = {"messages": messages}
    state = self.graph.summarize(initial_state)
    state = self.graph.search_vector_db(state, k)
    location_details = state["location_details"]
    return location_details
  
  def get_location_details_by_id(self, location_id: str) -> dict:
    """Truy xuất thông tin chi tiết từ MongoDB dựa trên location_id."""
    try:
      docs = fetch_from_mongodb([location_id], URL="vietnamtourism_URL", collection="vietnamtourism_db", document="vietnamtourism_db")
      #if not docs or not docs[0]:
      #  return {"error": f"No data found for location_id {location_id}"}
            
      doc = docs[0]
      data = doc.get('data', {})
      return {
        "_id": str(doc.get("_id")),
        "name": data.get('name', ''),
        "category": data.get('category', '').lower(),
        "address": data.get('address', ''),
        "description": data.get('description', '')
      }
    except Exception as e:
      return {"error": f"Error fetching data for location_id {location_id}: {str(e)}"}

  def get_location_response(self, location_id: str) -> str:
    """
    Tạm thời bây giờ, câu response sẽ là câu mô tả
    """
    try:
      details = self.get_location_details_by_id(location_id)
      # Kiểm tra nếu có lỗi
      if "error" in details:
        return details["error"]
      
      # Trả về mô tả nếu có
      description = details.get("description", "")
      return description if description else "Đây là địa điểm phù hợp với yêu cầu của bạn."
      
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
  suggestion_service = SuggestionService(faiss_name="v20250506_153250")
  location_ids = suggestion_service.get_location_ids(messages, k=20)
  print("Location IDs:", location_ids)

  for sample_id in location_ids:
    details = suggestion_service.get_location_details_by_id(sample_id)
    print("\nInformation for ID", sample_id)
    print("Location name", details["name"])
    print("Location address", details["address"])


  for sample_id in location_ids:
    location_response = suggestion_service.get_location_response(sample_id)
    print("\nLocation Response for ID", sample_id, ":", location_response)
