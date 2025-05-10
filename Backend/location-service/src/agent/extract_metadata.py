from bson import ObjectId
import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service")))
from data_interface import MongoDB
def fetch_from_mongodb(db: MongoDB, id_strs = []):
    object_ids = [ObjectId(_id) for _id in id_strs]

    # Truy vấn bằng $in
    docs = list(db.find({"_id": {"$in": object_ids}}))
    return docs