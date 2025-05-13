import random
import json
import os

# Định nghĩa các danh sách
categories = ["Công viên", "Nhà hàng", "Chùa", "Hồ", "Bãi biển", "Quán cafe", "Di tích", "Chợ", "Rừng", "Thác", "Đảo", "Khu du lịch"]
activities = ["ngắm cảnh", "ăn uống", "trekking", "chụp ảnh", "tắm biển", "uống cafe", "khám phá", "cắm trại"]
sao = ["1 sao", "1.5 sao", "2 sao", "2.5 sao", "3 sao", "3.5 sao", "4 sao", "4.5 sao", "5 sao"]
gia_thanh = ["giá rẻ", "giá thấp", "giá trung bình", "giá cao", "giá cao cấp"]
loai_so_huu = ["thiên nhiên", "tư nhân", "nhà nước", "cộng đồng"]
loai_hinh = [
    "khu du lịch", "bảo tàng", "di tích", "biển", "hồ", "lăng", "đền", 
    "nhà thờ", "cầu", "phố cổ", "làng nghề", "núi", "suối", "hang động", 
    "khu nghỉ dưỡng", "sông", "đồi cát", "rừng", "thác", "đảo", "chợ", 
    "công viên", "nhà hàng", "quán cafe", "bến cảng", "thị trấn"
]
van_hoa = [
    "tâm linh", "thủ công", "di sản văn hóa", "lễ hội", "truyền thống", 
    "nghệ thuật", "âm nhạc", "kiến trúc cổ", "ẩm thực", "tín ngưỡng"
]
prefixes = ["Vườn", "Khu", "Bãi", "Đền", "Chùa", "Nhà", "Làng", "Cầu", "Suối", "Hồ", "Rừng", "Thác", "Đảo", "Phố"]
suffixes = ["Xanh", "Cổ", "Lớn", "Nhỏ", "Trăng", "Sáng", "Vàng", "Đẹp", "Hoang", "Thơ", "Mộng", "Huyền", "Thanh"]

# Đọc dữ liệu từ file addresses.txt
addresses = []
with open("addresses.txt", "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split(",")
        if len(parts) == 4:
            map_id, ward, district, province = parts
            addresses.append({
                "map_id": map_id,
                "ward": ward,
                "district": district,
                "province": province
            })

# Đọc dữ liệu từ map_id.json
with open("map_id.json", "r", encoding="utf-8") as f:
    map_id_data = json.load(f)

# Đọc dữ liệu từ province.json
with open("province.json", "r", encoding="utf-8") as f:
    province_data = json.load(f)

# Tạo mock data
mock_data = []
for i in range(10000):
    # Chọn một địa chỉ ngẫu nhiên từ addresses
    address_info = random.choice(addresses)
    map_id = address_info["map_id"]
    ward = address_info["ward"]
    district = address_info["district"]
    province = address_info["province"]

    # Lấy thông tin tỉnh từ map_id.json
    region_key = map_id_data.get(map_id)

    # Lấy tọa độ và thông tin vùng từ province.json
    province_info = province_data.get(region_key, {})
    coordinates = province_info.get("coordinates")
    #image_url =  province_info.get("image_url")
    image_url = "https://cellphones.com.vn/sforum/wp-content/uploads/2024/01/dia-diem-du-lich-o-ha-noi-1.jpg"
    latitude = str(round(coordinates[0], 6))
    longitude = str(round(coordinates[1], 6))

    # Chọn danh mục
    category = random.choice(categories)

    # Tạo tên tự nhiên
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    name = f"{prefix} {suffix} {province}" if random.random() > 0.3 else f"{category} {prefix} {suffix}"

    # Tạo địa chỉ chi tiết
    address = f"{ward}, {district}, {province}"

    # Tạo category chi tiết theo định dạng [sao] [giá thành] [loại sở hữu] [loại hình] [văn hóa]
    sao_value = random.choice(sao) if random.random() > 0.5 else ""
    gia_thanh_value = random.choice(gia_thanh) if random.random() > 0.3 else ""
    loai_so_huu_value = random.choice(loai_so_huu)
    loai_hinh_value = random.choice(loai_hinh)
    van_hoa_value = random.choice(van_hoa) if random.random() > 0.5 else ""
    category_detail = ",".join(filter(None, [
        sao_value, gia_thanh_value, loai_so_huu_value, loai_hinh_value, van_hoa_value
    ]))

    # Tạo mô tả phong phú
    activity1 = random.choice(activities)
    activity2 = random.choice([act for act in activities if act != activity1])
    description = (
        f"{name} nằm tại {province}, là một {category.lower()} nổi bật với {random.choice(['cảnh quan thiên nhiên', 'kiến trúc cổ kính', 'hệ sinh thái đa dạng', 'không gian yên bình'])}. "
        f"Khu vực này thu hút du khách nhờ {random.choice(['vẻ đẹp tự nhiên', 'lịch sử lâu đời', 'văn hóa đặc sắc', 'trải nghiệm độc đáo'])}. "
        f"Du khách có thể {activity1} và {activity2} trong không gian {random.choice(['thoải mái', 'bình yên', 'hùng vĩ', 'tràn ngập ánh sáng'])}. "
        f"Nơi đây phù hợp cho những ai muốn {random.choice(['thư giãn', 'khám phá thiên nhiên', 'tìm hiểu văn hóa', 'trải nghiệm mới'])}."
    )

    # Tạo ID
    _id = f"6820a1bc3dd0a2e345dc{i:05d}"

    # Tạo bản ghi dữ liệu
    mock_data.append({
        "_id": _id,
        "type": "Location",
        "data": {
            "name": name,
            "category": category_detail,
            "address": address,
            "description": description,
            "latitude": latitude,
            "longitude": longitude,
            "image_url": image_url
        },
        "location": {
            "type": "Point",
            "coordinates": [float(longitude), float(latitude)]
        },
    })

# In thử một bản ghi để kiểm tra
print(json.dumps(mock_data[0], ensure_ascii=False, indent=2))