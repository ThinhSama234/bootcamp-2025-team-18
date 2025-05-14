import uuid
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../agent")))
from extract_metadata import fetch_from_mongodb
from graph import Graph

def get_coordinates_by_province(province_name):
    provinces = {
      "Bắc Giang": {"coordinates": [21.333333, 106.333333]},
      "Bắc Kạn": {"coordinates": [22.166667, 105.833333]},
      "Cao Bằng": {"coordinates": [22.666667, 106]},
      "Hà Giang": {"coordinates": [22.75, 105]},
      "Lạng Sơn": {"coordinates": [21.75, 106.5]},
      "Phú Thọ": {"coordinates": [21.333333, 105.166667]},
      "Quảng Ninh": {"coordinates": [21.25, 107.333333]},
      "Thái Nguyên": {"coordinates": [21.666667, 105.833333]},
      "Tuyên Quang": {"coordinates": [21.666667, 105.833333]},
      "Lào Cai": {"coordinates": [22.333333, 104]},
      "Yên Bái": {"coordinates": [21.5, 104.666667]},
      "Điện Biên": {"coordinates": [21.383333, 103.016667]},
      "Hòa Bình": {"coordinates": [20.333333, 105.25]},
      "Lai Châu": {"coordinates": [22, 103]},
      "Sơn La": {"coordinates": [21.166667, 104]},
      "Bắc Ninh": {"coordinates": [21.083333, 106.166667]},
      "Hà Nam": {"coordinates": [20.583333, 106]},
      "Hải Dương": {"coordinates": [20.916667, 106.333333]},
      "Hưng Yên": {"coordinates": [20.833333, 106.083333]},
      "Nam Định": {"coordinates": [20.25, 106.25]},
      "Ninh Bình": {"coordinates": [20.25, 105.833333]},
      "Thái Bình": {"coordinates": [20.5, 106.333333]},
      "Vĩnh Phúc": {"coordinates": [21.3, 105.6]},
      "Hà Nội": {"coordinates": [21.028472, 105.854167]},
      "Hải Phòng": {"coordinates": [20.865139, 106.683833]},
      "Hà Tĩnh": {"coordinates": [18.333333, 105.9]},
      "Nghệ An": {"coordinates": [19.333333, 104.833333]},
      "Quảng Bình": {"coordinates": [17.5, 106.333333]},
      "Quảng Trị": {"coordinates": [16.75, 107]},
      "Thanh Hóa": {"coordinates": [20, 105.5]},
      "Thừa Thiên - Huế": {"coordinates": [16.333333, 107.583333]},
      "Đắk Lắk": {"coordinates": [12.666667, 108.05]},
      "Đắk Nông": {"coordinates": [11.983333, 107.7]},
      "Gia Lai": {"coordinates": [13.75, 108.25]},
      "Kon Tum": {"coordinates": [14.75, 107.916667]},
      "Lâm Đồng": {"coordinates": [11.95, 108.433333]},
      "Bình Định": {"coordinates": [14.166667, 109]},
      "Bình Thuận": {"coordinates": [10.933333, 108.1]},
      "Khánh Hòa": {"coordinates": [12.25, 109.2]},
      "Ninh Thuận": {"coordinates": [11.75, 108.833333]},
      "Phú Yên": {"coordinates": [13.166667, 109.166667]},
      "Quảng Nam": {"coordinates": [15.583333, 107.916667]},
      "Quảng Ngãi": {"coordinates": [15, 108.666667]},
      "Đà Nẵng": {"coordinates": [16.066667, 108.233333]},
      "Bà Rịa - Vũng Tàu": {"coordinates": [10.583333, 107.25]},
      "Bình Dương": {"coordinates": [11.166667, 106.666667]},
      "Bình Phước": {"coordinates": [11.75, 106.916667]},
      "Đồng Nai": {"coordinates": [11.116667, 107.183333]},
      "Tây Ninh": {"coordinates": [11.333333, 106.166667]},
      "Hồ Chí Minh": {"coordinates": [10.776889, 106.700806]},
      "An Giang": {"coordinates": [10.5, 105.166667]},
      "Bạc Liêu": {"coordinates": [9.25, 105.75]},
      "Bến Tre": {"coordinates": [10.166667, 106.5]},
      "Cà Mau": {"coordinates": [9.083333, 105.083333]},
      "Đồng Tháp": {"coordinates": [10.666667, 105.666667]},
      "Hậu Giang": {"coordinates": [9.783333, 105.466667]},
      "Kiên Giang": {"coordinates": [10, 105.166667]},
      "Long An": {"coordinates": [10.666667, 106.166667]},
      "Sóc Trăng": {"coordinates": [9.666667, 105.833333]},
      "Tiền Giang": {"coordinates": [10.416667, 106.166667]},
      "Trà Vinh": {"coordinates": [9.833333, 106.25]},
      "Vĩnh Long": {"coordinates": [10.166667, 106]},
      "Cần Thơ": {"coordinates": [10.033333, 105.783333]}
    }
    return provinces.get(province_name, {}).get("coordinates")

class SuggestionService:
  def __init__(self, faiss_name: str = None):
    self.graph = Graph(faiss_name)
    
  def get_session_id(self) -> str:
    return str(uuid.uuid4())

  def get_location_ids(self, k: int, messages: list[str]) -> list[str]: # done
    initial_state = {"messages": messages}
    state = self.graph.summarize(initial_state)
    state = self.graph.search_vector_db(state, k)
    location_details = state["location_details"]
    #print("Tên tỉnh:", state["entities"])
    #print("Tọa độ tỉnh:", get_coordinates_by_province(state["entities"]["provinces"][0]))
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
      "Tôi muốn đi du lịch đến Vũng Tàu.",
      #"Ở miền Nam thì càng tốt.",
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
  location_ids = suggestion_service.get_location_ids(k=20, messages=messages)
  print("Location IDs:", location_ids)

  for sample_id in location_ids:
    details = suggestion_service.get_location_details_by_id(sample_id)
    print("\nInformation for ID", sample_id)
    print("Location name", details["name"])
    print("Location address", details["address"])


  for sample_id in location_ids:
    location_response = suggestion_service.get_location_response(sample_id)
    print("\nLocation Response for ID", sample_id, ":", location_response)
