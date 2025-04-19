from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from data_interface import MongoDB  # Giả sử lớp MongoDB ở file database.py

app = FastAPI()

# Khởi tạo Location DB
location_db = MongoDB("mongodb://127.0.0.1:27017", "travel_db", "locations")

# Model cho yêu cầu API
class LocationFilter(BaseModel):
    category: str | None = None
    name: str | None = None

# API gợi ý địa điểm
@app.post("/suggestLocation")
async def suggest_location(filter: LocationFilter):
    try:
        # Tạo bộ lọc cho truy vấn
        query = {}
        if filter.category:
            query["data.category"] = filter.category
        if filter.name:
            query["data.name"] = {"$regex": filter.name, "$options": "i"}  # Tìm kiếm gần đúng

        # Truy xuất địa điểm từ Location DB
        records, error = location_db.find_records("location", query)
        if error:
            raise HTTPException(status_code=500, detail=str(error))

        # Chuyển đổi dữ liệu trả về
        locations = [
            {
                "id": str(record["_id"]),
                "name": record["data"].get("name"),
                "latitude": record["data"].get("latitude"),
                "longitude": record["data"].get("longitude"),
                "category": record["data"].get("category"),
            }
            for record in records
        ]

        return {"locations": locations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suggest locations: {e}")

# API lưu địa điểm mới
@app.post("/addLocation")
async def add_location(location: Dict[str, Any]):
    try:
        record = {
            "type": "location",
            "data": location
        }
        record_id, error = location_db.save_record(record)
        if error:
            raise HTTPException(status_code=500, detail=str(error))
        return {"id": record_id, "message": "Location saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save location: {e}")

# Đóng kết nối khi ứng dụng tắt
@app.on_event("shutdown")
def shutdown_event():
    location_db.close()