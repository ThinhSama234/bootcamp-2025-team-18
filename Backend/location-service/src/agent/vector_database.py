import os
import json
from pathlib import Path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service")))
from vector_store.vectordb import VectorDB
from dotenv import load_dotenv
from vector_store.version_manager import get_version_timestamp
from data_interface import MongoDB
from bson import ObjectId
from json_loader import load_json_data
def ingest_data_to_vector_db(db):
    manager = VectorDB()
    faiss_name = get_version_timestamp()

    total_ingested = 0
    for dest in db.collection.find({}):
        try:
            if dest:
                # Lấy các trường cần thiết từ metadata
                _id = dest.get("_id")
                data = dest.get('data', {})
                name = data.get('name', '')
                address = data.get('address', '')
                description = data.get('description', '')
                merged_text = f"{name} {address} {description}"
                result = manager.ingest(
                    source=merged_text,
                    faiss_name=faiss_name,
                    _id = _id
                )
                print(f"✅ Ingested: {result}")
                total_ingested += 1
        except Exception as e:
            print(f"❌ Error ingesting text: {str(e)}")


    print(f"Total destinations ingested: {total_ingested}")
    with open("faiss_name.txt", "w") as f:
        f.write(faiss_name)
    return faiss_name

def ingest_data_to_vector_db_json():
    manager = VectorDB()
    faiss_name = get_version_timestamp()

    data_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service/crawl_data/Data")))
    print(f"Data directory: {data_dir}")
    json_files = ["vietnamtourism_db.vietnamtourism_db.json"]

    merged_texts = load_json_data(data_dir, json_files)
    total_ingested = 0
    for merged_text in merged_texts:
        try:
            result = manager.ingest(
                source=merged_text["merged_text"],
                faiss_name=faiss_name,
                _id=merged_text["_id"],
            )
            print(f"✅ Ingested: {result}")
            total_ingested += 1
        except Exception as e:
            print(f"❌ Error ingesting text: {str(e)}")
    print(f"Total destinations ingested: {total_ingested}")
    with open("faiss_name.txt", "w") as f:
        f.write(faiss_name)
    return faiss_name

if __name__ == "__main__":
    load_dotenv()
    # Load MongoDB URI từ biến môi trường
    DB_URL = os.getenv("vietnamtourism_URL")
    if not DB_URL:
        raise Exception("vietnamtourism_URL is not set in environment variables")

    # Khởi tạo kết nối MongoDB
    db = MongoDB(DB_URL, "vietnamtourism_db", "vietnamtourism_db")
    #faiss_name = ingest_data_to_vector_db_json()
    faiss_name = ingest_data_to_vector_db(db)
    print(f"Completed ingestion with faiss_name: {faiss_name}")
