from bson import ObjectId

from database.data_interface import MongoDB

def fetch_from_mongodb(db: MongoDB, id_strs = []):
    object_ids = [ObjectId(_id) for _id in id_strs]

    # Truy vấn bằng $in
    docs = list(db.find({"_id": {"$in": object_ids}}))
    return docs