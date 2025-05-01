import os
import json
from pathlib import Path
import sys
from json_loader import load_json_data
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service/vector_store")))
from vectordb import VectorDB

from version_manager import get_version_timestamp

def ingest_data_to_vector_db():
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
    for merged_text in merged_texts:
        try:
            result = manager.ingest(
                source=merged_text,
                faiss_name=faiss_name
            )
            print(f"✅ Ingested: {result}")
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

if __name__ == "__main__":
    faiss_name = ingest_data_to_vector_db()
    print(f"Completed ingestion with faiss_name: {faiss_name}")
        
