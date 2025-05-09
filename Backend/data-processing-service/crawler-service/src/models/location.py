from pydantic import BaseModel, Field
from typing import List

class LocationData(BaseModel):
    """ Location data model """
    name: str = Field(..., description="Tên của địa điểm")
    address: str = Field(..., description="Địa chỉ của địa điểm")
    description: str = Field(..., description="Mô tả về địa điểm")
    category: str = Field(default="", description="Phân loại địa điểm với định dạng (nếu không có thì thôi): '[sao] [giá thành] [loại sở hữu] [loại hình] [văn hóa]', ví dụ: '4.5 sao, giá cao, thiên nhiên, khu du lịch, tâm linh'")
    latitude: str = Field(default="", description="Vĩ độ của địa điểm")
    longitude: str = Field(default="", description="Kinh độ của địa điểm")
    image_url: List[str] = Field(default=[], description="URL của hình ảnh địa điểm")

class Location(BaseModel):
    """ Location model """
    type: str = Field(..., description="Loại đối tượng, ví dụ: 'Location', 'Restaurant', 'Hotel'")
    data: LocationData = Field(..., description="Thông tin chi tiết của địa điểm")


