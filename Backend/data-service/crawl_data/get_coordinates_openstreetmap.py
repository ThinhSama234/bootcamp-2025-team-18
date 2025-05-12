import requests
import time
from pymongo import MongoClient
import os
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_interface import MongoDB
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry 
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))
def clean_name(line: str):
    # Bỏ số 1 ở cuối nếu có, loại bỏ khoảng trắng thừa
    cleaned = line.strip()
    if cleaned.endswith(" 1"):
        cleaned = cleaned[:-2].strip()
    return cleaned
def adjusted_coordinates(URL = "TRAVELDB_URL", db_name= "travel_db", collection_name= "auto_crawl"):
    db = MongoDB(URL, db_name, collection_name)  # để lưu lat/lon
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "MyTravelVietNam/1.0 (truongthinh2301@gmail.com)"  
    }
    i = 1
    try:
        for line in db.collection.find():
            print("đang ở document thứ", i)
            i = i + 1
            location = line.get("type")
            idd = line.get("_id")
            name = line.get("data", {}).get("name")
            address = line.get("data", {}).get("address")
            category = line.get("data", {}).get("category")
            description = line.get("data", {}).get("description")
            image_url = line.get("data", {}).get("image_url")
            if name is None:
                name = line.get("name")
                address = line.get("address")
                category = line.get("category")
                description = line.get("description")
                image_url = line.get("image_url")
            if name is None:
                print(f"[❌] Missing name for document ID: {idd}")
                continue
            if address is None:
                print(f"[❌] Missing address for document ID: {idd}")
                continue
            if description is None:
                print(f"[❌] Missing description for document ID: {idd}")
                continue
            latitude = line.get("data", {}).get("latitude")
            if latitude is None or type(latitude) != str or category is None or latitude == "" or latitude == ".":
                print(f"[❌] Missing latitude for document ID: {idd}, {address}")
                list_try_address = extract_province_and_district(address)
                for try_address in list_try_address:
                    print("dia chi tim trong openstreetmap", try_address)
                    # lấy data từ MongoDB
                    params = {
                        "q": try_address,
                        "format": "json",
                        "limit": 1
                    }
                    response = session.get(url, params=params, headers=headers)
                    time.sleep(1)
                    if response.status_code == 200:
                        results = response.json()
                        if results:
                            info = {
                            "latitude": str(results[0]["lat"]),
                            "longitude": str(results[0]["lon"]),
                            "display_name": results[0]["display_name"],
                            "type": results[0]["type"]
                            }

                            print("lat", info["latitude"])
                            print("lon", info["longitude"])
                            print("display_name", info["display_name"])
                            print("type", info["type"])
                            if category is None:
                                category = info["type"]
                            record = {
                                "_id": idd,
                                "type": location,
                                "data": {
                                    "name": name,
                                    "address": address,
                                    "latitude": info["latitude"],
                                    "longitude": info["longitude"],
                                    "category": category,
                                    "description": description,
                                    "image_url": image_url
                                }
                            }
                            # Lưu vào MongoDB
                            record_id, error = db.update_record(record)
                            print("record_id", record_id)
                            if error:
                                print(f"[❌] Failed: {name}. Error: {error}")
                            else:
                                print(f"[✅] Saved: {name} -> ID: {record_id}")
                                break
                        else:
                            print(f"[❌] {name}: Không tìm thấy.")
                    else:
                        print(f"[🚫] Lỗi HTTP: {response.status_code} cho {name}") 
    finally:
        print("Tổng số documents:", db.count_documents({}))
        db.close()
    return None
def extract_province_and_district(address: str) -> list:
    """Cắt địa chỉ dần dần từ đầy đủ -> tỉnh, huyện"""
    parts = address.split(",")
    results = []
    for i in range(len(parts)):
        result = ", ".join(parts[i:]).strip()
        #print(f"[🔁] Địa chỉ thử: {result}")
        if result and result not in results:
            results.append(result)
    return results
def create_location_coordinates(URL="TRAVELDB_URL", db_name="travel_db", collection_name="auto_crawl"):
    db = MongoDB(URL, db_name, collection_name)
    i = 1
    
    try:
        for line in db.collection.find():
            print("đang ở document thứ", i)
            i += 1
            _id = line.get("_id")
            data = line.get("data", {})
            type_ = line.get("type", "location")  # Giả sử type mặc định là "location"

            # Lấy thông tin từ data, xử lý trường hợp thiếu dữ liệu
            name = data.get("name")
            address = data.get("address", '')
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            category = data.get("category", '')
            description = data.get("description", '')
            image_url = data.get("image_url", '')

            # Kiểm tra nếu latitude và longitude tồn tại và là số
            if latitude is None or longitude is None:
                print(f"[⚠️] Bỏ qua {_id}: Thiếu hoặc không phải số cho latitude ({latitude}) hoặc longitude ({longitude}).")
                continue
            try:
                lat = float(latitude)
                lon = float(longitude)
            except (ValueError, TypeError) as e:
                print(f"[⚠️] Bỏ qua {_id}: Không thể ép kiểu latitude ({latitude}) hoặc longitude ({longitude}) sang số. Lỗi: {e}")
                continue
            # Tạo updated_record
            updated_record = {
                "_id": _id,  # Sử dụng _id từ tài liệu hiện tại
                "type": type_,
                "data": {
                    "name": name,
                    "address": address,
                    "latitude": latitude,
                    "longitude": longitude,
                    "category": category,
                    "description": description,
                    "image_url": image_url
                },
                "location": {  # Thêm trường location với kiểu Point
                    "type": "Point",
                    "coordinates": [float(lon), float(lat)]  # Chuyển sang float để đảm bảo định dạng
                }
            }

            # Cập nhật vào MongoDB
            updated_id, error = db.update_record(updated_record)
            print("record_id", updated_id)
            if error:
                print(f"[❌] Failed: {name}. Error: {error}")
            else:
                print(f"[✅] Saved: {name} -> ID: {updated_id}")
            

    except Exception as e:
        print(f"[❌] Lỗi tổng quát: {e}")
    finally:
        db.close()
        print("Đã đóng kết nối MongoDB.")

    return None
def create_index_coordinates(URL="TRAVELDB_URL", db_name="travel_db", collection_name="auto_crawl"):
    db = MongoDB(URL, db_name, collection_name)
    #Tạo chỉ mục 2dsphere cho trường location
    db.collection.create_index([("location", "2dsphere")])
    print("Đã tạo chỉ mục 2dsphere cho trường location.")
    return

def check_address()-> bool:
    """Kiểm tra xem địa chỉ đã có trong MongoDB hay chưa"""
    DB_URL = os.getenv("TRAVELDB_URL")
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")
    db = MongoDB(DB_URL, "travel_db", "address")
    for line in db.collection.find():
        location = line.get("type")
        idd = line.get("_id")
        name = line.get("data", {}).get("name")
        address = line.get("data", {}).get("address")
        category = line.get("data", {}).get("category")
        description = line.get("data", {}).get("description")
        latitude = line.get("data", {}).get("latitude")
        longitude = line.get("data", {}).get("longitude")
        if name is None:
            print(f"[❌] Missing name for document ID: {idd}")
            return False
        if address is None:
            print(f"[❌] Missing address for document ID: {idd}")
            return False
        if category is None:
            print(f"[❌] Missing category for document ID: {idd}")
            return False
        if description is None:
            print(f"[❌] Missing description for document ID: {idd}")
            continue
        if latitude is None:
            print(f"[❌] Missing latitude for document ID: {idd}")
            return False
        if longitude is None:
            print(f"[❌] Missing longitude for document ID: {idd}")
            return False
    print("Tất cả các địa chỉ đã có trong MongoDB.")
    db.close()
    return True
if __name__ == "__main__":
    #check_address()
    uri = "mongodb+srv://truongthinh2301:tpuNNUBTBxrgOm1a@cluster0.dlrf4cw.mongodb.net/"
    #adjusted_coordinates(URL = uri, db_name="travel_db", collection_name="locations")
    create_location_coordinates( URL = uri, db_name="travel_db", collection_name="locations")
    #create_index_coordinates( URL = uri, db_name="travel_db", collection_name="locations")