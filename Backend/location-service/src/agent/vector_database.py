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

def ingest_data_to_vector_db(object_ids):
    manager = VectorDB()
    faiss_name = get_version_timestamp()

    data_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service/crawl_data/Data")))
    print(f"Data directory: {data_dir}")

    # json_files = [
    #     "baclieu_tourist_destinations.json",
    #     "bacninh_tourist_destinations.json",
    #     "danang_tourist_destinations.json",
    #     "haiphong_tourist_destinations.json",
    #     "hanoi_tourist_destinations.json",
    #     "hoian_tourist_destinations.json",
    #     "quangbinh_tourist_destinations.json",
    #     "quangnam_tourist_destinations (2).json",
    #     "saigon_tourist_destinations.json",
    #     "vungtau_tourist_destinations.json"
    # ]

    json_files = ["vietnamtourism_db.vietnamtourism_db.json"]

    merged_texts = load_json_data(data_dir, json_files)

    total_ingested = 0
    for json_file in json_files:
        file_path = data_dir / json_file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                destinations = json.load(f)

            for i, dest in enumerate(destinations):
                if i >= len(object_ids):
                    print(f"⚠️ Không đủ object_id để ánh xạ. Bỏ qua dòng {i}")
                    break
                #_id = "680d1faac29c10273910b825"
                _id = object_ids[i]
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
                print(f"✅ Ingested {name}: {result}")
                total_ingested += 1
        except Exception as e:
            print(f"❌ Error ingesting text: {str(e)}")


    print(f"Total destinations ingested: {total_ingested}")

    # print("\nSearching...")
    # try:
    #     results = manager.search(
    #         faiss_name=faiss_name,
    #         query="bình phước",
    #         top_k=3,
    #         threshold=0.6  # Ngưỡng similarity
    #     )
        
    #     for result in results:
    #         print(f"\n🔍 Score: {result['score']:.4f}")
    #         print(result['content'])
    #         print(result['source'])

    # except Exception as e:
    #     print(f"Search error: {str(e)}")
    with open("faiss_name.txt", "w") as f:
        f.write(faiss_name)
    return faiss_name

def fetch_from_mongodb(db, id_strs):
    # Convert sang ObjectId
    object_ids = [ObjectId(_id) for _id in id_strs]

    # Truy vấn bằng $in
    docs = list(db.find({"_id": {"$in": object_ids}}))
    return docs
if __name__ == "__main__":
    load_dotenv()
    # Load MongoDB URI từ biến môi trường
    DB_URL = os.getenv("vietnamtourism_URL")
    if not DB_URL:
        raise Exception("vietnamtourism_URL is not set in environment variables")

    # Khởi tạo kết nối MongoDB
    db = MongoDB(DB_URL, "vietnamtourism_db", "vietnamtourism_db")
    records = list(db.collection.find({}, {"_id": 1}))  # lấy danh sách _id
    object_ids = [str(record["_id"]) for record in records]
    faiss_name = ingest_data_to_vector_db(object_ids)
    print(f"Completed ingestion with faiss_name: {faiss_name}")
    # id_strs = []
    # id_strs.append("680ca1618372cda0a3d6adfd")
    # docs = fetch_from_mongodb(db, id_strs)
    # print(docs[0])
        
