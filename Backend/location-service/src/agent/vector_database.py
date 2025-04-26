import os
import json
from pathlib import Path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service/vector_store")))
from vectordb import VectorDB

from version_manager import get_version_timestamp

def ingest_data_to_vector_db():
    manager = VectorDB()
    faiss_name = get_version_timestamp()

    data_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service/crawl_data/Data")))
    print(f"Data directory: {data_dir}")

    json_files = [
        "baclieu_tourist_destinations.json",
        "bacninh_tourist_destinations.json",
        "danang_tourist_destinations.json",
        "haiphong_tourist_destinations.json",
        "hanoi_tourist_destinations.json",
        "hoian_tourist_destinations.json",
        "quangbinh_tourist_destinations.json",
        "quangnam_tourist_destinations (2).json",
        "saigon_tourist_destinations.json",
        "vungtau_tourist_destinations.json"
    ]

    for json_file in json_files:
        file_path = data_dir / json_file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                destinations = json.load(f)

            for dest in destinations:
                name = dest.get('name', '')
                address = dest.get('address', '')
                description = dest.get('description', '')
                merged_text = f"{name} {address} {description}"

                result = manager.ingest(
                    source=merged_text,
                    faiss_name=faiss_name
                )
                print(f"✅ Ingested {name}: {result}")
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")

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
    return faiss_name

if __name__ == "__main__":
    faiss_name = ingest_data_to_vector_db()
    print(f"Completed ingestion with faiss_name: {faiss_name}")
        
