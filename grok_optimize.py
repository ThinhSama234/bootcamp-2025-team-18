import os
from bson import ObjectId
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
import random
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from dotenv import load_dotenv
import threading

# Configuration
load_dotenv()
BATCH_SIZE = 5000  # Increased batch size
MAX_WORKERS = 30   # More concurrent workers
TOTAL_RECORDS = 100000
API_LIMIT = 0   # Records to process with API
threshold_grok = 0.5
threshold_api = 1
threshold_name = 1
# Initialize APIs
def init_apis():
    google_api_key = os.getenv("google_api")
    if not google_api_key:
        raise ValueError("Missing Google API key")
    client_google = genai.Client(api_key=google_api_key)
    
    grok_api_key = os.getenv("grok_api")
    if not grok_api_key:
        raise ValueError("Missing Grok API key")
    grok_client = OpenAI(
        api_key=grok_api_key,
        base_url="https://api.x.ai/v1",
    )
    return client_google, grok_client

client_google, grok_client = init_apis()

# Data loading optimized
def load_data():
    start = time.time()
    
    # Load addresses
    with open("addresses.txt", "r", encoding="utf-8") as f:
        addresses = [{
            "map_id": parts[0], "ward": parts[1], 
            "district": parts[2], "province": parts[3]
        } for line in f if len(parts := line.strip().split(",")) == 4]
    
    # Load JSON files
    with open("map_id.json", "r", encoding="utf-8") as f:
        map_id_data = json.load(f)
    
    with open("province.json", "r", encoding="utf-8") as f:
        province_data = json.load(f)
    
    print(f"Data loaded in {time.time()-start:.2f}s")
    return addresses, map_id_data, province_data

addresses, map_id_data, province_data = load_data()

# Constants
categories = ["Công viên", "Nhà hàng", "Chùa", "Hồ", "Bãi biển", "Quán cafe", "Di tích", "Chợ", "Rừng", "Thác", "Đảo", "Khu du lịch"]
activities = ["ngắm cảnh", "ăn uống", "trekking", "chụp ảnh", "tắm biển", "uống cafe", "khám phá", "cắm trại", "thể thao", "khám phá", "xem biểu diễn nghệ thuật", "học nấu ăn địa phương", "thử trang phục truyền thống", "tham gia lễ hội", "nghe nhạc dân gian", "thăm di tích lịch sử", "đi chợ đêm", "tắm bùn", "tắm onsen", "massage", "ngồi thiền", "tập yoga", "đọc sách bên hồ", "vẽ tranh", "viết nhật ký du lịch", "nghe podcast", "làm gốm", "chụp ảnh phong cảnh", "leo núi", "ngắm mây", "cắm trại"]
sao = ["1 sao", "1.5 sao", "2 sao", "2.5 sao", "3 sao", "3.5 sao", "4 sao", "4.5 sao", "5 sao"]
gia_thanh = ["rẻ", "giá thấp", "giá trung bình", "giá cao", "giá cao cấp"]
loai_so_huu = ["thiên nhiên", "do tư nhân mở", "nhà nước sở hữu"]
loai_hinh = ["khu du lịch", "bảo tàng", "di tích", "biển", "hồ", "lăng", "đền", "nhà thờ", "cầu", "phố cổ", "làng nghề", "núi", "suối", "hang động", "khu nghỉ dưỡng", "sông", "đồi cát", "rừng", "thác", "đảo", "chợ", "công viên", "nhà hàng", "quán cafe", "bến cảng", "thị trấn"]
van_hoa = ["tâm linh", "thủ công", "di sản văn hóa", "lễ hội", "truyền thống", "nghệ thuật", "âm nhạc", "kiến trúc cổ", "ẩm thực", "tín ngưỡng"]
# Manual description with enhanced variety
highlight_features = [
        "cảnh quan thiên nhiên", "kiến trúc truyền thống", "không gian yên bình", 
        "di sản văn hóa", "hệ sinh thái đa dạng", "lịch sử lâu đời", 
        "vị trí độc đáo", "khí hậu dễ chịu", "nét đặc trưng địa phương", 
        "khung cảnh thơ mộng", "bao quanh bởi rừng xanh và núi đá", "nằm bên dòng sông thơ mộng", 
        "gần các làng nghề truyền thống", "giữa thung lũng yên tĩnh", 
        "trên cao nguyên lộng gió", "giữa vùng đồng bằng trù phú", 
        "tựa vào vách núi hùng vĩ", "bên bờ biển cát trắng", 
        "trong khu vực di sản được bảo tồn", "giữa không gian đậm chất thôn quê"
    ]
visitor_activities_intro = [
    "Du khách có thể", "Khách tham quan có thể", "Nơi đây cho phép du khách", 
    "Bạn có thể", "Người đến thăm có thể"
]
target_audiences = [
    "những ai yêu thiên nhiên", "người đam mê văn hóa", "các nhà thám hiểm", 
    "gia đình tìm kiếm sự thư giãn", "người yêu thích lịch sử", 
    "những ai muốn trải nghiệm mới lạ", "du khách tìm kiếm sự yên bình", 
    "người muốn khám phá ẩm thực địa phương"
]
# Thread-safe resources
description_cache = {}
cache_lock = threading.Lock()
file_lock = threading.Lock()
def get_random_description_from_file():
    """
    Lấy ngẫu nhiên một mô tả từ file cache
    Trả về:
    - str: Nội dung mô tả nếu thành công
    - None: Nếu file không tồn tại hoặc có lỗi
    """
    try:
        with file_lock, open("description_cache_file.txt", "r", encoding="utf-8") as f:
            try:
                # Đọc toàn bộ file và parse JSON
                cached_items = [json.loads(line) for line in f if line.strip()]
                
                if not cached_items:
                    return None
                
                # Chọn ngẫu nhiên một mục
                random_item = random.choice(cached_items)
                return random_item.get("description")
                
            except json.JSONDecodeError as e:
                print(f"Lỗi parse JSON trong file cache: {e}")
                return None
                
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Lỗi không xác định khi đọc file cache: {e}")
        return None
def call_gemini_api_for_name(i, province, category):
    if random.random() > threshold_name: # 30% là dùng gemini
        try:
            prompt = (
                f"Tạo một tên địa điểm du lịch ngẫu nhiên tại '{province}' phù hợp với '{category}', theo mẫu: [Tiền tố] + [Tên chính] + [Hậu tố nếu có] + mã số '{i:05d}'. Chỉ trả về 1 dòng tên, không viết thêm gì khác."
            )
            response = client_google.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Lỗi khi gọi API gemini để tạo tên: {e}")
            # Fallback: Tạo tên thủ công
            prefixes = [
                "Chùa", "Hồ", "Bãi", "Núi", "Đền", "Thác", "Đảo", "Rừng", 
                "Suối", "Vịnh", "Biển", "Đồi", "Làng", "Thành", "Cổng", "Cầu",
                "Khu", "Vườn", "Động", "Hang", "Bến", "Phố", "Quảng", "Đình",
                "Miếu", "Am", "Tháp", "Đường", "Lăng", "Khe", "Bờ", "Ghềnh",
                "Gành", "Mũi", "Eo", "Đèo", "Cửa", "Bàu", "Mương", "Ruộng",
                "Cánh", "Triền", "Mạch", "Mỏ", "Bãi", "Bến", "Chợ", "Kênh"
                "Vực", "Lũng", "Cù", "Bồng", "Trũng", "Gò", "Sình", "Đầm", "Rọc", "Lạch",
                "Hẻm", "Ngõ", "Rú", "Mỏm", "Đụn", "Bồng", "Sông", "Khuynh", "Trảng", "Dốc",
                "Lèn", "Mép", "Đoạn", "Bìa", "Cánh", "Ranh", "Tổ", "Nổng", "Hốc", "Khoảnh"
            ]
            names = ["Thịnh", "Vàng", "Ngọc", "Rồng", "Phượng", "Hương", "Sơn", "Lý", "Thanh", "Huyền", "Trăng", "Thịnh", "Thái", "Khánh", "Hòa", "Lộc", "Phúc", "Tâm", "Đức", 
                "Tài", "Phú", "Quý", "Bình", "An", "Minh", "Sơn", "Hải",
                "Giang", "Long", "Phong", "Vũ", "Vân", "Ngọc", "Kim", "Bảo",
                "Châu", "Diệp", "Linh", "Mai", "Lan", "Cúc", "Trúc", "Liên",  "Bảo Lâm", "Hữu Tình", "Minh Khai", "Thiên Thanh", "Đức Thắng",
                "Quang Vinh", "Hồng Đăng", "Ngọc Lan", "Kim Liên", "Bạch Mai",
                "Thanh Tùng", "Hải Đăng", "Gia Bảo", "Mỹ Lệ", "Tuấn Anh",
                "Khánh Ly", "Hoàng Kim", "Ngọc Trinh", "Bảo Châu", "Minh Tuệ",
                "Thiên Phú", "Hồng Nhung", "Lam Giang", "Thanh Hà", "Xuân Mai",
                "Bích Ngọc", "Hương Giang", "Kim Chi", "Ngọc Ánh", "Thu Hà"
                "Ánh", "Băng", "Cẩm", "Chi", "Đan", "Dung", "Hạnh", "Hiên", "Hòa", "Huân",
                "Hùng", "Khang", "Khoa", "Khuê", "Kiên", "Lam", "Lâm", "Lệ", "Liễu", "Loan",
                "Lương", "Mẫn", "Nga", "Nghi", "Nghĩa", "Nhàn", "Nhi", "Nhung", "Oanh", "Phấn",
                "Phương", "Quân", "Quyên", "Sáng", "Sử", "Thắm", "Thảo", "Thiện", "Thịnh", "Thông",
                "Thùy", "Tiên", "Tín", "Tố", "Trâm", "Trân", "Triết", "Trúc", "Tuyền", "Uyên",
                "Việt", "Vinh", "Vỹ", "Xuân", "Yên", "Ân", "Bích", "Cường", "Diệu", "Đông",
                "Hiền", "Hợp", "Kỳ", "Lạc", "Mộng", "Nam", "Nhiên", "Phú", "Quang", "Sơn",
                "Tâm", "Thăng", "Thúy", "Tường", "Vân", "Vọng", "Ý", "Anh Thư", "Bích Thủy", 
                "Cẩm Tú", "Dạ Hương", "Đình Trung", "Hà My", "Hải Vân", "Hoài An", "Hồng Ngọc", 
                "Kim Ngân", "Lệ Thu", "Linh Chi", "Mỹ Dung", "Ngân Hà", "Nhật Minh", "Phương Thảo", 
                "Quốc Bảo", "Thanh Nhàn", "Thiên Kim", "Trúc Quỳnh", "Vân Anh", "Vĩnh Phúc", 
                "Xuân Hồng", "Yến Nhi"
                "Mộng Rêu", "Hàm Sương", "Vụng Nguyệt", "Tịch Dương", "Lãnh Vân", "Sa Mộng", "Huyền Không", "Nguyệt Rằm", "Thanh U", "Dạ Lữ",
                "Sương Bích", "Lộng Gió", "Mây Trôi", "Hà Lưu", "Bồng Lai", "Tử Yên", "Lục Hương", "Viễn Kiều", "Trầm Ngân", "Hồ Tiên",
                "Cẩm Sắc", "Vũ Điệp", "Tinh Thần", "Lưu Sa", "Ngọc Hư", "Phong Lãm", "Hải Mộng", "Thiên Tuyền", "Đạm Thanh", "Vô Thường",
                "Kỳ Hạc", "Bích Dao", "Lãm Nguyệt", "Tà Dương", "Hương Trầm", "Lộng Ảnh", "Tuyết Sương", "Vân Hạc", "Mộc Miên", "Thiên Di",
                "Lưu Huyền", "Ngân Sắc", "Hồng Trần", "Vũ Hành", "Tịch Mịch", "Lam Nguyệt", "Sơn Thủy", "Huyền Dạ", "Thanh Trúc", "Viễn Tâm"
                "Hạc Vời", "Tương Lai", "Mộng Điền", "Vân Thủy", "Lưu Ngấn", "Huyền Sắc", "Tịnh Yên", "Nguyệt Hư", "Sa Lung", "Thẩm Lãng",
                "Bích Huyền", "Phong Ngân", "Lãnh Tịch", "Hà Sương", "Tiên Lữ", "Dạ Hạc", "Lam Tuyền", "Viễn Sắc", "Trầm Vân", "Hồ Nguyệt",
                "Cẩm Lưu", "Vũ Tinh", "Hư Thanh", "Lộng Mộng", "Ngọc Tuyền", "Sơn Huyền", "Thiên Lãng", "Vân Di", "Tà Hương", "Lục Yên",
                "Kỳ Vân", "Thủy Ngân", "Miên Sương", "Hồng Hư", "Tịch Lưu", "Băng Nguyệt", "Hà Tinh", "Lãm Huyền", "Phong Di", "Thanh Vời",
                "Vụng Tâm", "Ngân Lữ", "Huyền Điền", "Sắc Lung", "Mộng Hư", "Tuyền Sương", "Vân Thẩm", "Lãng Yên", "Tinh Lãnh", "Dạ Vời"
                "Huyền Đăng", "Tử Sương", "Lãnh Hương", "Vân Lộc", "Tinh Hư", "Mộng Tuyền", "Sa Hạc", "Nguyệt Di", "Thẩm Thanh", "Dạ Lung",
                "Bích Lãng", "Phong Tịch", "Hà Vời", "Lưu Tinh", "Tiên Ngân", "Viễn Huyền", "Lam Sắc", "Trầm Lữ", "Hồ Thủy", "Cẩm Yên",
                "Vũ Nguyệt", "Hư Lộng", "Sơn Mộng", "Ngọc Lãng", "Thiên Hạc", "Tà Tuyền", "Vân Sương", "Lục Hư", "Tịch Ngân", "Băng Di",
                "Kỳ Lưu", "Thủy Huyền", "Miên Thanh", "Hồng Vời", "Lãm Sắc", "Tuyết Tinh", "Vân Lãnh", "Phong Hương", "Thanh Lung", "Vụng Hạc",
                "Ngân Mộng", "Huyền Tịch", "Sắc Viễn", "Mộng Vân", "Tuyền Lãng", "Lưu Sương", "Tinh Yên", "Dạ Hương", "Vời Nguyệt", "Thẩm Di"
                ]
            suffixes = [
                "Xanh", "Cổ", "Lớn", "Nhỏ", "Trăng", "Vàng", "Bạc", "Đỏ",
                "Hồng", "Tím", "Lam", "Bích", "Ngọc", "Kim", "Thiêng", "Thần",
                "Tiên", "Rồng", "Phượng", "Lân", "Quy", "Phụng", "Mây", "Gió",
                "Nắng", "Mưa", "Sương", "Mai", "Đào", "Cúc", "Lan", "Huệ",
                "Trầm", "Bổng", "Cao", "Thấp", "Dài", "Ngắn", "Rộng", "Hẹp",
                "Mới", "Cũ", "Đông", "Tây", "Nam", "Bắc", "Xuân", "Hạ",
                "Thu", "Đông", "Mơ", "Thực", "Đá", "Nước", "Lửa", "Gió",
                "Cát", "Sỏi", "Đất", "Trời", "Mặt Trời", "Mặt Trăng", "Sao"
                "Vời", "Hư", "Lãng", "Tịnh", "Di", "Lữ", "Hạc", "Ngân", "Tuyền", "Sắc",
                "Lộng", "Yên", "Viễn", "Huyền", "Lưu", "Tinh", "Mộng", "Lãnh", "Thẩm", "Vụng",
                "Thanh", "Băng", "Kỳ", "Miên", "Tà", "Lục", "Cẩm", "Phong", "Hồng", "Nguyệt"
            ]
            prefix = random.choice(prefixes)
            name_count = random.randint(1, 3)
            main_name = " ".join(random.choices(names, k=name_count))
            suffix = random.choice(suffixes) if random.random() > 0.5 else ""
            return f"{prefix} {main_name} {suffix} {i:05d}".strip()
    else:
        prefixes = [
            "Chùa", "Hồ", "Bãi", "Núi", "Đền", "Thác", "Đảo", "Rừng", 
            "Suối", "Vịnh", "Biển", "Đồi", "Làng", "Thành", "Cổng", "Cầu",
            "Khu", "Vườn", "Động", "Hang", "Bến", "Phố", "Quảng", "Đình",
            "Miếu", "Am", "Tháp", "Đường", "Lăng", "Khe", "Bờ", "Ghềnh",
            "Gành", "Mũi", "Eo", "Đèo", "Cửa", "Bàu", "Mương", "Ruộng",
            "Cánh", "Triền", "Mạch", "Mỏ", "Bãi", "Bến", "Chợ", "Kênh"
        ]
        names = ["Thịnh", "Vàng", "Ngọc", "Rồng", "Phượng", "Hương", "Sơn", "Lý", "Thanh", "Huyền", "Trăng", "Thịnh", "Thái", "Khánh", "Hòa", "Lộc", "Phúc", "Tâm", "Đức", 
            "Tài", "Phú", "Quý", "Bình", "An", "Minh", "Sơn", "Hải",
            "Giang", "Long", "Phong", "Vũ", "Vân", "Ngọc", "Kim", "Bảo",
            "Châu", "Diệp", "Linh", "Mai", "Lan", "Cúc", "Trúc", "Liên",  "Bảo Lâm", "Hữu Tình", "Minh Khai", "Thiên Thanh", "Đức Thắng",
            "Quang Vinh", "Hồng Đăng", "Ngọc Lan", "Kim Liên", "Bạch Mai",
            "Thanh Tùng", "Hải Đăng", "Gia Bảo", "Mỹ Lệ", "Tuấn Anh",
            "Khánh Ly", "Hoàng Kim", "Ngọc Trinh", "Bảo Châu", "Minh Tuệ",
            "Thiên Phú", "Hồng Nhung", "Lam Giang", "Thanh Hà", "Xuân Mai",
            "Bích Ngọc", "Hương Giang", "Kim Chi", "Ngọc Ánh", "Thu Hà",
            "Ánh", "Băng", 
            "Hùng", "Khang", 
            "Lương", "Mẫn", "Nga", "Nghi", "Nghĩa", "Nhàn", 
            "Phương", "Quân", "Quyên", "Sáng", "Sử", "Thắm", "Thảo", "Thiện", "Thịnh", "Thông",
            "Thùy", "Tiên", "Tín", "Tố", "Trâm", "Trân", "Triết", "Trúc", "Tuyền", "Uyên",
            "Việt", "Vinh", "Vỹ", "Xuân", "Yên", "Ân", "Bích", "Cường", "Diệu", "Đông",
            "Hiền", "Hợp", "Kỳ", "Lạc", "Mộng", "Nam", "Nhiên", "Phú", "Quang", "Sơn",
            "Tâm", "Thăng", "Thúy", "Bích Thủy", 
            "Cẩm Tú", "Dạ Hương", "Đình Trung", "Hà My", "Hải Vân", "Hoài An", "Hồng Ngọc", 
            "Ngân Hà", "Nhật Minh", "Phương Thảo", 
            "Quốc Bảo", "Thanh Nhàn", "Thiên Kim", "Trúc Quỳnh", "Vân Anh", "Vĩnh Phúc", 
            "Xuân Hồng", "Yến Nhi",
            "Mộng Rêu", "Hàm Sương", "Vụng Nguyệt", "Tịch Dương", "Lãnh Vân", "Sa Mộng", "Huyền Không", "Nguyệt Rằm", "Thanh U", "Dạ Lữ",
            "Sương Bích", "Lộng Gió", "Mây Trôi", "Hà Lưu", "Bồng Lai", "Tử Yên", "Lục Hương", "Viễn Kiều", "Trầm Ngân", "Hồ Tiên",
            "Cẩm Sắc", "Vũ Điệp", "Tinh Thần", "Lưu Sa", "Ngọc Hư", "Phong Lãm", "Hải Mộng", "Thiên Tuyền", "Đạm Thanh", "Vô Thường",
            "Kỳ Hạc", "Bích Dao", "Lãm Nguyệt", "Tà Dương", "Hương Trầm", "Lộng Ảnh", "Tuyết Sương", "Vân Hạc", "Mộc Miên", "Thiên Di",
            "Lưu Huyền", "Ngân Sắc", "Hồng Trần", "Vũ Hành", "Tịch Mịch", "Lam Nguyệt", "Sơn Thủy", "Huyền Dạ", "Thanh Trúc", "Viễn Tâm"
            "Hạc Vời", "Tương Lai", "Mộng Điền", "Vân Thủy", "Lưu Ngấn", "Huyền Sắc", "Tịnh Yên", "Nguyệt Hư", "Sa Lung", "Thẩm Lãng",
            "Bích Huyền", "Phong Ngân", "Lãnh Tịch", "Hà Sương", "Tiên Lữ", "Dạ Hạc", "Lam Tuyền", "Viễn Sắc", "Trầm Vân", "Hồ Nguyệt",
            "Cẩm Lưu", "Vũ Tinh", "Hư Thanh", "Lộng Mộng", "Ngọc Tuyền", "Sơn Huyền", "Thiên Lãng", "Vân Di", "Tà Hương", "Lục Yên",
            "Kỳ Vân", "Thủy Ngân", "Miên Sương", "Hồng Hư", "Tịch Lưu", "Băng Nguyệt", "Hà Tinh", "Lãm Huyền", "Phong Di", "Thanh Vời",
            "Vụng Tâm", "Ngân Lữ", "Huyền Điền", "Sắc Lung", "Mộng Hư", "Tuyền Sương", "Vân Thẩm", "Lãng Yên", "Tinh Lãnh", "Dạ Vời"
            "Huyền Đăng", "Tử Sương", "Lãnh Hương", "Vân Lộc", "Tinh Hư", "Mộng Tuyền", "Sa Hạc", "Nguyệt Di", "Thẩm Thanh", "Dạ Lung",
            "Bích Lãng", "Phong Tịch", "Hà Vời", "Lưu Tinh", "Tiên Ngân", "Viễn Huyền", "Lam Sắc", "Trầm Lữ", "Hồ Thủy", "Cẩm Yên",
            "Vũ Nguyệt", "Hư Lộng", "Sơn Mộng", "Ngọc Lãng", "Thiên Hạc", "Tà Tuyền", "Vân Sương", "Lục Hư", "Tịch Ngân", "Băng Di",
            "Kỳ Lưu", "Thủy Huyền", "Miên Thanh", "Hồng Vời", "Lãm Sắc", "Tuyết Tinh", "Vân Lãnh", "Phong Hương", "Thanh Lung", "Vụng Hạc",
            "Ngân Mộng", "Huyền Tịch", "Sắc Viễn", "Mộng Vân", "Tuyền Lãng", "Lưu Sương", "Tinh Yên", "Dạ Hương", "Vời Nguyệt", "Thẩm Di"
            ]
        suffixes = [
            "Xanh", "Cổ", "Lớn", "Nhỏ", "Trăng", "Vàng", "Bạc", "Đỏ",
            "Hồng", "Tím", "Lam", "Bích", "Ngọc", "Kim", "Thiêng", "Thần",
            "Tiên", "Rồng", "Phượng", "Lân", "Quy", "Phụng", "Mây", "Gió",
            "Nắng", "Mưa", "Sương", "Mai", "Đào", "Cúc", "Lan", "Huệ",
            "Trầm", "Bổng", "Cao", "Thấp", "Dài", "Ngắn", "Rộng", "Hẹp",
            "Mới", "Cũ", "Đông", "Tây", "Nam", "Bắc", "Xuân", "Hạ",
            "Thu", "Đông", "Mơ", "Thực", "Đá", "Nước", "Lửa", "Gió",
            "Cát", "Sỏi", "Đất", "Trời", "Sao"
        ]
        prefix = random.choice(prefixes)
        name_count = random.randint(1, 3)
        main_name = " ".join(random.choices(names, k=name_count))
        suffix = random.choice(suffixes) if random.random() > 0.5 else ""
        return f"{prefix} {main_name} {suffix} {i:05d}".strip()
# Optimized description generation
def generate_description(data_entry, use_api=True):
    cache_key = f"{data_entry['name']}"
    sample_description = get_random_description_from_file()
    try:
        if use_api and random.random() > threshold_api:  # Use API for 20% of cases
            if random.random() > threshold_grok:  # Use Grok 50% of API cases
                response = grok_client.chat.completions.create(
                model="grok-3-mini-beta",
                messages=[
                    {"role": "system", "content": "You are a travel writer."},
                    {"role": "user", "content": (
                        f"Tạo một mô tả 4-5 câu bằng tiếng Việt cho địa điểm du lịch '{data_entry['name']}' tại '{data_entry['province']}'. "
                        f"Đây là một {data_entry['category'].lower()} với các hoạt động như {', '.join(data_entry['activities'])}. "
                        f"Mô tả cần tập trung vào đặc trưng địa điểm, hệ sinh thái, trải nghiệm, và lý do chọn, "
                        f"tránh từ ngữ chủ quan như 'tuyệt vời', 'đẹp nhất'. Ngôn ngữ tự nhiên, khách quan."
                    )}
                ],
                temperature=0.7,
                max_tokens=1000
                )
                desc = response.choices[0].message.content.strip()
                # Save to cache
                with cache_lock:
                    description_cache[cache_key] = desc
            else:  # Use Gemini
                prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a travel writer. Given a sample description, transform it into a new description using the provided name, address, category, and activities. "
                        "Keep the structure and style of the sample description (4-5 sentences) with objective information: focus on the location's standout features, ecosystem, notable experiences, and reasons to choose it. "
                        "Avoid subjective phrases (e.g., 'wonderful', 'amazing') and promotional content (e.g., 'MIA.vn', 'will bring you great experiences'). "
                        "Language will be Vietnamese. "
                        "Ensure the address follows the format: '<ward>, <district>, tỉnh <province>'."
                    ),
                    ("human", "Sample description: {sample_description}\nNew details: Name: {name}, Address: {address}, Category: {category}, Activities: {activities}"),
                ]
                )
                try:
                    formatted_prompt = prompt.format_prompt(
                        sample_description=sample_description,
                        name=data_entry["name"],
                        address=data_entry["address"],
                        category=data_entry["category"],
                        activities=data_entry["activities"],
                    ).to_string()
                except Exception as e:
                    raise ValueError(f"Lỗi khi tạo formatted_prompt: {e}")
                response = client_google.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
                )
                desc = response.text.strip()
        else:
            # Manual description
            # sample_description cắt tới dấu chấm đầu tiên để bỏ tỉnh, của thằng trước
            description_part = ""
            if sample_description:
                # Xử lý sample_description như cached_descriptions
                parts = sample_description.split('.', 1)  # Tách tại dấu chấm đầu tiên
                if len(parts) > 1 and parts[1].strip():
                    description_part = parts[1].strip() + ". "
                else:
                    description_part = sample_description.strip() + ". "
            else:
                # Fallback nếu không có sample_description
                description_part = "Nơi đây mang đến không gian độc đáo với nhiều trải nghiệm hấp dẫn. "
            
            activities = " và ".join(data_entry['activities'])
            province = data_entry['province']

            desc = (
                f"{data_entry['name']} tại {data_entry['address']}, "
                f"nổi bật với {random.choice(highlight_features)}. "
                f"{description_part.capitalize()}"  # Tích hợp description_part
                f"{random.choice(visitor_activities_intro)} {activities}. "
                f"Địa điểm này phù hợp với {random.choice(target_audiences)} "
                f"và những ai muốn khám phá nét độc đáo của {province}."
            )
            
        
        return desc
    except Exception:
        # Manual description
        # sample_description cắt tới dấu chấm đầu tiên để bỏ tỉnh, của thằng trước
        description_part = ""
        if sample_description:
            # Xử lý sample_description như cached_descriptions
            parts = sample_description.split('.', 1)  # Tách tại dấu chấm đầu tiên
            if len(parts) > 1 and parts[1].strip():
                description_part = parts[1].strip() + ". "
            else:
                description_part = sample_description.strip() + ". "
        else:
            # Fallback nếu không có sample_description
            description_part = "Nơi đây mang đến không gian độc đáo với nhiều trải nghiệm hấp dẫn. "
        activities = " và ".join(data_entry['activities'])
        province = data_entry['province']

        desc = (
            f"{data_entry['name']} tại {data_entry['address']}, "
            f"nổi bật với {random.choice(highlight_features)}. "
            f"{description_part.capitalize()}"  # Tích hợp description_part
            f"{random.choice(visitor_activities_intro)} {activities}. "
            f"Địa điểm này phù hợp với {random.choice(target_audiences)} "
            f"và những ai muốn khám phá nét độc đáo của {province}."
        )
        return desc

# Batch processing
def process_batch(batch_indices):
    results = []
    
    def process_item(i):
        address = random.choice(addresses)
        province_info = province_data.get(map_id_data.get(address["map_id"]), {})
        coords = province_info.get("coordinates", ["0", "0"])
        
        category = random.choice(categories)
        sao_value = random.choice(sao) if random.random() > 0.5 else ""
        gia_thanh_value = random.choice(gia_thanh) if random.random() > 0.3 else ""
        loai_so_huu_value = random.choice(loai_so_huu)
        loai_hinh_value = random.choice(loai_hinh)
        van_hoa_value = random.choice(van_hoa) if random.random() > 0.5 else ""
        category_detail = ", ".join(filter(None, [
            sao_value, gia_thanh_value, loai_so_huu_value, loai_hinh_value, van_hoa_value
        ]))
        name = call_gemini_api_for_name(i, address["province"], category)
        
        # Create data entry
        data = {
            "_id": str(ObjectId()),
            "type": "Location",
            "data": {
                "name": name,
                "category": category_detail,
                "address": f"{address['ward']}, {address['district']}, {address['province']}",
                "latitude": coords[1],
                "longitude": coords[0],
                "image_url": province_info.get("image_url", []),
                "description": ""  # Will be filled later
            },
            "location": {
                "type": "Point",
                "coordinates": [float(coords[0]), float(coords[1])]
            }
        }
        activitie = random.sample(activities, 2)
        # Generate description
        data["data"]["description"] = generate_description({
            "name": name,
            "province": address["province"],
            "address": data["data"]["address"],
            "activities": activitie,
            "category": category_detail,
        }, use_api=i < API_LIMIT)
        
        return data
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_item, i) for i in batch_indices]
        for future in as_completed(futures):
            results.append(future.result())
    
    return results

# Main execution
def main():
    start_time = time.time()
    all_data = []
    
    # Try to load existing data
    try:
        with file_lock, open("travel_locations.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            processed_count = len(existing_data)
            all_data.extend(existing_data)
    except (FileNotFoundError, json.JSONDecodeError):
        processed_count = 0
    
    print(f"Starting from record {processed_count}")
    # Process in batches
    for batch_start in range(0, TOTAL_RECORDS, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TOTAL_RECORDS)
        print(f"Processing batch {batch_start}-{batch_end-1}...")
        
        batch_time = time.time()
        batch_data = process_batch(range(batch_start, batch_end))
        all_data.extend(batch_data)
        #print("all data hien co:", len(all_data))
        # Save progress
        if batch_end % (BATCH_SIZE * 5) == 0 or batch_end == TOTAL_RECORDS:
            with file_lock, open("travel_locations.json", "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            # Save cache
            with file_lock, open("description_cache_file.txt", "a", encoding="utf-8") as f:
                for name, desc in description_cache.items():
                    if desc and desc.strip() and desc != "Mô tả đang được cập nhật.":
                        f.write(json.dumps({"name": name, "description": desc}, ensure_ascii=False) + "\n")
                description_cache.clear()
        
        print(f"Batch completed in {time.time()-batch_time:.2f}s")
    
    print(f"Finished {TOTAL_RECORDS} records in {time.time()-start_time:.2f}s")

if __name__ == "__main__":
    main()