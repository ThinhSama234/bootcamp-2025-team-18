import requests
import time
from pymongo import MongoClient
import os
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from data_interface import MongoDB 
load_dotenv()
def clean_name(line: str):
    # Bỏ số 1 ở cuối nếu có, loại bỏ khoảng trắng thừa
    cleaned = line.strip()
    if cleaned.endswith(" 1"):
        cleaned = cleaned[:-2].strip()
    return cleaned
def adjusted_text(file_path: str):
    DB_URL = os.getenv("TRAVELDB_URL")
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")

    db = MongoDB(DB_URL, "travel_db", "location_address")
    with open(file_path, "r", encoding="utf-8") as f: 
        lines = f.readlines()
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "MyTravelVietNam/1.0 (truongthinh2301@gmail.com)"  
    }
    i = 1
    for line in lines:
        if i<=1176:
            i = i + 1
            continue
        if line.strip() == "" or line.startswith("http"):
            continue
        name = clean_name(line)
        params = {
            "q": name,
            "format": "json",
            "limit": 1
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            results = response.json()
            if results:
                info = {
                    "name": name,
                    "lat": results[0]["lat"],
                    "lon": results[0]["lon"],
                    "display_name": results[0]["display_name"],
                    "type": results[0]["type"]
                }
                print(f"[✅] {name}: {info}")
                record_id, error = db.save_record(info)
                if error:
                    print(f"[❌] Failed: {name}. Error: {error}")
                else:
                    print(f"[✅] Saved: {name} -> ID: {record_id}")
            else:
                print(f"[❌] {name}: Không tìm thấy.")
        else:
            print(f"[🚫] Lỗi HTTP: {response.status_code} cho {name}")
        time.sleep(1) 
    print("Tổng số documents:", db.count_documents({}))
    db.close()
    return None
def extract_province_and_district(address: str) -> str:
    """Cắt địa chỉ chỉ giữ lại tỉnh và huyện"""
    parts = address.split(",")
    if len(parts) >= 2:
        return ", ".join(parts[-2:]).strip()
    if len(parts) >= 3:
        return ", ".join(parts[-3:]).strip()
    return address.strip()

def update_address(file_path):
    DB_URL = os.getenv("TRAVELDB_URL")
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")

    db = MongoDB(DB_URL, "travel_db", "location_address")  # để lưu lat/lon
    db1 = MongoDB(DB_URL, "vietnamtourism_db", "vietnamtourism_db")        # chứa name và address

    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "MyTravelVietNam/1.0 (truongthinh2301@gmail.com)"
    }

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if line.strip() == "" or line.startswith("http"):
            continue

        name = clean_name(line)

        # Check nếu name đã có trong location_address rồi thì bỏ qua
        if db.find_one({"name": name}):
            print(f"[⏭️] Đã có: {name}")
            continue

        # Tìm address trong collection locations
        location_doc = db1.find_one({"data.name": name})
        if not location_doc:
            print(f"[❌] Không tìm thấy địa điểm {name} trong collection 'locations'")
            continue

        address = location_doc.get("data", {}).get("address")
        if not address:
            print(f"[❌] {name} không có địa chỉ.")
            continue

        # Hàm gọi API nominatim
        def fetch_geodata(q):
            params = {
                "q": q,
                "format": "json",
                "limit": 1
            }
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                result = response.json()
                return result[0] if result else None
            else:
                print(f"[🚫] Lỗi HTTP: {response.status_code} cho {name}")
                return None

        # Thử lần 1 với địa chỉ đầy đủ
        geo = fetch_geodata(address)

        # Nếu không có thì thử lại với tỉnh, huyện
        if not geo:
            simplified_address = extract_province_and_district(address)
            print(f"[🔁] Địa chỉ không tìm thấy. Thử lại với: {simplified_address}")
            geo = fetch_geodata(simplified_address)

        if geo:
            info = {
                "name": name,
                "lat": geo["lat"],
                "lon": geo["lon"],
                "display_name": geo["display_name"],
                "type": geo["type"]
            }
            record_id, error = db.save_record(info)
            if error:
                print(f"[❌] Lỗi khi lưu {name}: {error}")
            else:
                print(f"[✅] Đã lưu: {name} -> ID: {record_id}")
        else:
            print(f"[❌] Không tìm thấy toạ độ cho {name}.")

        time.sleep(1)  # delay tránh bị rate-limit

    print("Tổng số documents:", db.count_documents({}))
    db.close()

def update_address_hotels(file_path):
    DB_URL = os.getenv("TRAVELDB_URL")
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")

    db = MongoDB(DB_URL, "vietnamtourism_db", "restaurant")  # Collection location_address chỉ cập nhật tọa độ
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "MyTravelVietNam/1.0 (truongthinh2301@gmail.com)"
    }
    i = 1
    for line in db.collection.find():
        if i<=1673:
            i = i+1
            continue
        address = line.get("data", {}).get("address")
        print("dia chi goc", address)
        name = line.get("data", {}).get("name")
        if not address:
            print(f"[❌] {name} không có địa chỉ.")
            continue

        # Hàm gọi API nominatim
        def fetch_geodata(q):
            params = {
                "q": q,
                "format": "json",
                "limit": 1
            }
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                result = response.json()
                return result[0] if result else None
            else:
                print(f"[🚫] Lỗi HTTP: {response.status_code} cho {name}")
                return None

        # Thử lần 1 với địa chỉ đầy đủ
        geo = fetch_geodata(address)

        # Nếu không có thì thử lại với tỉnh, huyện
        if not geo:
            simplified_address = extract_province_and_district(address)
            print(f"[🔁] Địa chỉ không tìm thấy. Thử lại với: {simplified_address}")
            geo = fetch_geodata(simplified_address)

        if geo:
            # Cập nhật lại tọa độ vào collection location_address
            update_result = db.collection.update_one(
                {"data.name": name},  # Truy cập vào trường lồng nhau
                {"$set": {
                    "data.lat": geo["lat"],  # Cập nhật vào bên trong `data`
                    "data.lon": geo["lon"]
                }}
            )
            print("du lieu bi thay doi hay chua", update_result.matched_count)
            if update_result.matched_count > 0:
                print(f"[✅] Đã cập nhật tọa độ cho: {name}")
            else:
                print(f"[❌] Không tìm thấy khách sạn {name} để cập nhật tọa độ.")
        else:
            print(f"[❌] Không tìm thấy toạ độ cho {name}.")

        time.sleep(1)  # delay tránh bị rate-limit

    print("Tổng số documents:", db.count_documents({}))
    db.close()
if __name__ == "__main__":
    update_address_hotels("location_name.txt")