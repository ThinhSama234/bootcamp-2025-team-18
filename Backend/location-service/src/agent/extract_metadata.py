from bson import ObjectId
import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service")))
from data_interface import MongoDB
def fetch_from_mongodb(id_strs = [], URL = "TRAVELDB_URL", collection = "travel_db", document = "locations"):
    # Convert sang ObjectId
    load_dotenv()
        # Load MongoDB URI từ biến môi trường
    #DB_URL = os.getenv("TRAVELDB_URL")
    DB_URL = os.getenv(URL)
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")
    # Khởi tạo kết nối MongoDB
    db = MongoDB(DB_URL, collection, document)
    object_ids = [ObjectId(_id) for _id in id_strs]

    # Truy vấn bằng $in
    docs = list(db.find({"_id": {"$in": object_ids}}))
    db.close()
    print("✅ thành công, db đã đóng")
    return docs