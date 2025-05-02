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
def save_location_names(file_path: str):
    DB_URL = os.getenv("TRAVELDB_URL")
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")

    db = MongoDB(DB_URL, "travel_db", "location_names")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if line.strip() == "" or line.startswith("http"):
            continue
        name = clean_name(line)
        record = {
            "type": "location",
            "data": {
                "name": name,
                "address": None,
                "description": None,
                "image_url": None,
                "category": None,
            }
        }
        record_id, error = db.save_record(record)
        if error:
            print(f"[❌] Failed: {name}. Error: {error}")
        else:
            print(f"[✅] Saved: {name} -> ID: {record_id}")
    print("Tổng số documents:", db.count_documents({}))
    db.close()
def update_locations_from_json(json_file_path: str):
    DB_URL = os.getenv("TRAVELDB_URL")
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")

    db = MongoDB(DB_URL, "travel_db", "location_names")

    with open(json_file_path, "r", encoding="utf-8") as f:
        locations = json.load(f)
    updated_count = 0
    for loc in locations:
        name = loc.get("name")
        if not name:
            continue
        result = db.collection.update_one(
            {"type": "location", "name": name},
            {"$set": {
                "address": loc.get("address"),
                "description": loc.get("description"),
                "image_url": loc.get("image_url"),
                "category": loc.get("category")
            }}
        )
        count = result.modified_count
        if count:
            updated_count += 1
            print(f"[✅] Updated: {name}")
        else:
            print(f"[⚠️] Not found or not updated: {name}")

    print(f"✅ Tổng số địa danh đã cập nhật: {updated_count}")
    db.close()
if __name__ == "__main__":
    save_location_names("location_name.txt")