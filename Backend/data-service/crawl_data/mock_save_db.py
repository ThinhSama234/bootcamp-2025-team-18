
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_interface import MongoDB 
import os
from dotenv import load_dotenv

# Tạo dữ liệu JSON cho 3 địa điểm
locations = [
    {
        "name": "Trảng Cỏ Bù Lạch",
        "address": "Thôn 7, xã Đồng Nai, huyện Bù Đăng, tỉnh Bình Phước, Việt Nam",
        "description": (
            "Trảng Cỏ Bù Lạch là một thảo nguyên rộng khoảng 500 ha, bao gồm gần 20 trảng cỏ lớn nhỏ nằm giữa "
            "rừng nguyên sinh và hồ nước trong xanh. Nơi đây nổi bật với thảm cỏ kim xanh mướt, điểm xuyết hoa dại "
            "màu tím, tạo nên khung cảnh thơ mộng và hoang sơ. Khí hậu mát mẻ quanh năm, thích hợp cho các hoạt động "
            "cắm trại, dã ngoại và khám phá thiên nhiên."
        ),
        "image_url": "https://tse3.mm.bing.net/th?id=OIP.w3Gngig-IiMeqb4bw0NTUwHaFD&pid=Api"
    },
    {
        "name": "Vườn Quốc Gia Bù Gia Mập",
        "address": "Xã Bù Gia Mập, huyện Bù Gia Mập, tỉnh Bình Phước, Việt Nam",
        "description": (
            "Vườn Quốc Gia Bù Gia Mập là khu bảo tồn thiên nhiên rộng hơn 25.000 ha, nằm ở vùng chuyển tiếp giữa "
            "Tây Nguyên và Đông Nam Bộ. Nơi đây sở hữu hệ sinh thái đa dạng với hơn 700 loài thực vật và nhiều loài "
            "động vật quý hiếm như vượn đen má vàng, voọc chà vá chân đen. Du khách có thể trải nghiệm các hoạt động "
            "như trekking, khám phá thác nước, bãi đá Voi và cắm trại giữa thiên nhiên hoang dã."
        ),
        "image_url": "https://tse4.mm.bing.net/th?id=OIP.-eTdCqZC6vQ4gtWiRtRm_gHaFT&pid=Api"
    },
    {
        "name": "Hồ Suối Giai",
        "address": "Xã Tân Lập, huyện Đồng Phú, tỉnh Bình Phước, Việt Nam",
        "description": (
            "Hồ Suối Giai là hồ nước nhân tạo lớn với diện tích mặt nước trải rộng giữa những rừng cao su và đồi núi "
            "xanh tươi. Với cảnh quan yên bình, nơi đây là điểm đến lý tưởng để nghỉ dưỡng cuối tuần, câu cá và dã ngoại. "
            "Đặc biệt, khi hoàng hôn buông xuống, mặt hồ phẳng lặng phản chiếu bầu trời tạo nên khung cảnh thơ mộng, "
            "rất được lòng các tín đồ 'sống chậm'."
        ),
        "image_url": "https://tse1.mm.bing.net/th?id=OIP.QkuSn8OQNDecR1bZXlk4VAHaEK&pid=Api"
    }
]

locations1 = [
    {
        "name": "Thác Dambri",
        "address": "Xã Đamb'ri, thành phố Bảo Lộc, tỉnh Lâm Đồng, Việt Nam",
        "description": "Thác Dambri cao khoảng 70m, là một trong những thác nước đẹp và hùng vĩ nhất Tây Nguyên. Bao quanh là khu rừng nguyên sinh xanh mướt, khí hậu mát lạnh quanh năm. Du khách có thể đi thang máy ngắm thác từ trên cao, hoặc đi bộ theo bậc đá để khám phá dòng thác từ chân đến đỉnh.",
        "image_url": "https://tse3.mm.bing.net/th?id=OIP.uvdxtDxkU-fkyoNeYzSPkQHaE8&pid=Api"
    },
    {
        "name": "Đồi Cát Nam Cương",
        "address": "Xã An Hải, huyện Ninh Phước, tỉnh Ninh Thuận, Việt Nam",
        "description": "Đồi Cát Nam Cương nằm cách trung tâm thành phố Phan Rang khoảng 8 km. Nơi đây nổi bật với những triền cát trải dài bất tận, thay đổi hình dạng theo gió. Vào buổi sớm hoặc hoàng hôn, khung cảnh nơi đây trở nên huyền ảo, rất lý tưởng để chụp ảnh và trải nghiệm cưỡi lạc đà.",
        "image_url": "https://tse2.mm.bing.net/th?id=OIP.v_fOSz_QGrXvQXn6MoYv3QHaEo&pid=Api"
    },
    {
        "name": "Hồ Lắk",
        "address": "Xã Liên Sơn, huyện Lắk, tỉnh Đắk Lắk, Việt Nam",
        "description": "Hồ Lắk là hồ nước ngọt lớn thứ hai ở Tây Nguyên, bao quanh bởi những cánh rừng và bản làng của người M’nông. Tại đây, du khách có thể chèo thuyền độc mộc, cưỡi voi xuyên rừng hoặc nghỉ dưỡng tại các nhà dài truyền thống. Hồ Lắk còn là nơi lưu giữ nhiều nét văn hóa đặc trưng của người bản địa.",
        "image_url": "https://tse4.mm.bing.net/th?id=OIP.S9bCrLuNDO-C1UphqMfYagHaE7&pid=Api"
    }
]


load_dotenv()

def save_locations_from_json(file_path: str):
    # Load MongoDB URI từ biến môi trường
    # DB_URL = os.getenv("TRAVELDB_URL")
    # if not DB_URL:
    #     raise Exception("TRAVELDB_URL is not set in environment variables")

    # # Khởi tạo kết nối MongoDB
    # db = MongoDB(DB_URL, "travel_db", "locations")

    # Đọc dữ liệu từ file JSON
    with open(file_path, "r", encoding="utf-8") as f:
        locations = json.load(f)

    # Gửi từng record lên Mongo
    for loc in locations:
        # record = {
        #     "type": "location",
        #     "data": {
        #         "name": loc.get("name"),
        #         "address": loc.get("address"),
        #         "discription": loc.get("discription"),
        #         # "image_url": loc.get("image_url"),
        #         # "category": loc.get("category"),
        #     }
        # }
        name = loc.get("data", {}).get("name")
        address = loc.get("data", {}).get("address")
        discription = loc.get("data", {}).get("discription") 
        if name is None:
            print(f"Skipping record due to missing name: {loc}")
            continue
        with open("location_hotels.txt", "a", encoding="utf-8") as f:
            f.write(name + "\n")
        # record_id, error = db.save_record(record)
        # if error:
        #     print(f"[❌] Error saving: {loc['name']}. Reason: {error}")
        # else:
        #     print(f"[✅] Saved {loc['name']} with ID: {record_id}")
    # in ra số lượng documents hiện tại trong database
    # print("Số lượng documents hiện tại:", db.count_documents({}))
    # db.close()
    print("MongoDB connection closed.")
if __name__ == "__main__":
    # file_path = "Data/dia_diem_du_lich_binh_phuoc.json"
    # folder_path = os.path.join(os.path.dirname(__file__), "Data")
    # print(folder_path)
    # # Kiểm tra nếu thư mục Data tồn tại
    # if not os.path.exists(folder_path):
    #     raise Exception("The 'Data' folder does not exist!")
    # for file_name in os.listdir(folder_path):
    #     if file_name.endswith(".json"):
    #         file_path = os.path.join(folder_path, file_name)
    #         save_locations_from_json(file_path)
    file_path = "vietnamtourism_db.restaurant.json"
    save_locations_from_json(file_path)