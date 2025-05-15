import sys
import os
import traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_interface import MongoDB
from config.config import TRAVELDB_URL
uri = TRAVELDB_URL
db = MongoDB(uri, database="travel_db", collection="location_plus")
db_vector = MongoDB(uri, database="travel_db", collection="locations_vector_plus")
from vectordb import VectorDB
manager = VectorDB()
try:
    i = 0
    for record in db.collection.find():
        i += 1
        if record.get("data"):
            print(f"ở dòng thứ {i}")
            if (record.get("data").get("latitude") and record.get("data").get("longitude")) and (record.get("data").get("latitude") != "" and record.get("data").get("longitude")!= "") and (record.get("data").get("latitude") != "." and record.get("data").get("longitude")!= "."):
                lat = record.get("data").get("latitude")
                lon = record.get("data").get("longitude")
                record['location'] = {
                "type": "Point",
                "coordinates": [float(lat), float(lon)]
                }
            _id = record.get("_id")
            data = record.get('data', {})
            name = data.get('name', '')
            address = data.get('address', '')
            description = data.get('description', '')
            category = data.get('category', '')
            merged_text = f"{name} {address} {category} {description}".strip()
            embedding = manager.embed_texts([merged_text])[0].tolist()
            queue_item = {
                "type": record["type"],
                "embedding": embedding,
                "id_mongo": str(_id),
            }
            db_vector.save_record(queue_item)
except Exception as e:
    print("Bug:", e)
    #traceback.print_exc() 