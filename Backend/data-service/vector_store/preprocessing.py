from dotenv import load_dotenv
import os
load_dotenv()
print("Current Working Directory:", os.getcwd())
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data-service")))
from data_interface import MongoDB
from vector_store.vectordb import VectorDB
from vector_store.version_manager import get_version_timestamp
import numpy as np
try:
    DB_URL = os.environ.get('TRAVELDB_URL')
    db = MongoDB(DB_URL, "travel_db", "locations")
except Exception as e:
    print(f"Error initializing MongoDB: {e}")
# db.db # db.collection
# khởi tạo source
manager = VectorDB()
model = manager.embedding_model
mock_data = {
"name": "Trảng Cỏ Bù Lạch",
"address": "Thôn 7, xã Đồng Nai, huyện Bù Đăng, tỉnh Bình Phước, Việt Nam",
"description": "Trảng Cỏ Bù Lạch là một thảo nguyên rộng khoảng 500 ha...",
"image_url": "https://tse3.mm.bing.net/th?id=OIP.w3Gngig-IiMeqb4bw0NTUwHaFD&pid=Api"
}    
name_encode = mock_data['name']
address_encode = mock_data['address']
description_encode = mock_data['description']
faiss_name = get_version_timestamp()
merge_text = name_encode + " " + address_encode + " " + description_encode
print(merge_text)
try:
    result = manager.ingest(
        source=merge_text,
        faiss_name=faiss_name,
    )
    print(f"Data ingested successfully.")
except Exception as e:
     print(f"❌ Error processing {merge_text}: {str(e)}")
# search
print("🔎 Tìm kiếm theo entities:")
try:
    results = manager.search(
        faiss_name=faiss_name,
        query="Bình phước",
        top_k=1,
        threshold=0.6  # Ngưỡng similarity
    )
    
    for result in results:
        print(f"\n🔍 Score: {result["score"]:.4f}")
        print(result["content"])
        print(result["source"])

except Exception as e:
    print(f"Search error: {str(e)}")
for items in db.collection.find():
    print(items)
    break