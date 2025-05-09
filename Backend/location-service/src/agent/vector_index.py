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
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel
import time

def ingest_data_to_vector_db(db: MongoDB, db1: MongoDB):
    manager = VectorDB()
    faiss_name = get_version_timestamp()
    total_ingested = 0
    results = []
    for dest in db.collection.find({}):
        try:
            if dest:
                # Lấy các trường cần thiết từ metadata
                _id = dest.get("_id")
                data = dest.get('data', {})
                name = data.get('name', '')
                address = data.get('address', '')
                description = data.get('description', '')
                category = data.get('category', '')
                merged_text = f"{name} {address} {category} {description}".strip()
                print(f"Processing: {merged_text[:50]}...")
                # list embedding 
                result = manager.ingest_embedding(
                    source=merged_text,
                    faiss_name=faiss_name,
                    _id = str(_id)
                )
                # nối vào results
                results.extend(result)
                print(f"✅ Ingested: {result}")
                total_ingested += 1
                break
        except Exception as e:
            print(f"❌ Error ingesting text: {str(e)}")
    for res in results:
        print(res)
        record = {
            "type":"location",
            "embedding": res["embedding"],
            "id_mongo": res["mongo_id"],
        }
        # record_id, error = db1.save_record(record)
        # if error:
        #     print(f"Error saving record: {error}")
        # else:
        #     print(f"Successfully saved record with ID: {record_id}")
    print(f"Total destinations ingested: {total_ingested}")
    return
def create_search_index(db: MongoDB):
    # Create your index model, then create the search index
    search_index_model = SearchIndexModel(
    definition = {
        "fields": [
        {
            "type": "vector",
            "path": "embedding",
            "similarity": "cosine",
            "numDimensions": 384
            #"quantization": "scalar"
        }
        ]
    },
    name="vector_index",
    type="vectorSearch"
    )
    index_result = db.collection.create_search_index(model=search_index_model)
    print("New search index named " + index_result + " is building.")
    # Wait for initial sync to complete
    print("Polling to check if the index is ready. This may take up to a minute.")
    while True:
        indices = list(db.collection.list_search_indexes())
        if indices and indices[0].get("queryable") is True:
            break
        time.sleep(5)
    print("vector_index is ready for querying.")
    
    # Đóng kết nối
    db.client.close()

def search(db: MongoDB, query_text: str = "", top_k: int = 5):
    manager = VectorDB()
    query_vector = manager.embed_query(query_text).tolist()
    print(f"Mocked query vector created: {query_vector[0][:5]}...")
    pipeline = [
    {
        '$vectorSearch': {
        'index': 'vector_index', 
        'path': 'embedding', 
        'queryVector': query_vector[0], 
        'numCandidates': 150, 
        'limit': top_k,
        'scoreDetails': True,
        }
    },
    {
            "$addFields": {
                "score": {"$meta": "vectorSearchScore"}  # Thêm trường score
            }
    },
    {
            "$project": {
                "_id": 0,
                "embedding": 1,
                "id_mongo": 1,
                "score": 1
            }
    }]

    results = list(db.collection.aggregate(pipeline))
    if not results:
        print("No matches found.")
        return []
    
    print(f"Found {len(results)} matches:")
    #for res in results:
    #    print(f"ID: {res['id_mongo']}, Score: {res.get('score', 'N/A')}")
    return results
if __name__ == "__main__":
    uri = "mongodb+srv://truongthinh2301:tpuNNUBTBxrgOm1a@cluster0.dlrf4cw.mongodb.net/"
    db = MongoDB(uri, "travel_db", "locations")
    db1 = MongoDB(uri, "travel_db", "locations_vector")
    # Ingest dữ liệu
    #results = ingest_data_to_vector_db(db, db1)
    
    # # Tạo search index
    #create_search_index(db1)
    
    # Tìm kiếm mock
    query_text = "tôi muốn đi du lịch hà nội, thăm thú chùa một cột, vì tôi yêu di sản văn hóa"
    search_results = search(db1, query_text, top_k=3)
    print("Search results:", search_results)
    
