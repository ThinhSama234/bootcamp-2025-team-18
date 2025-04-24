import subprocess
import json
import re
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from typing import List, Dict, Optional
import datetime
class OllamaTourismProcessor:
    def __init__(self, ollama_path: str, model_name: str = "mistral"):
        self.ollama_path = ollama_path
        self.model_name = model_name
        
        self.TOURISM_TEMPLATE = """<<SYS>>
Bạn là một hệ thống AI, chỉ xuất ra JSON, không trả lời bất kỳ thông tin gì khác ngoài JSON.

Dưới đây là thông tin địa điểm. Dựa trên thông tin đầu vào, hãy trả về một JSON với các thông tin như sau:

{input_data}

Thông tin cần trả về trong định dạng JSON:

```json
{{
    "name": "{name}",
    "address": "{address}",
    "category": "{category}",
    "coordinates": {coordinates},
    "description": "{description}",
    "image_url": "{image_url}",
    "type": "location"
}}
"""
    def call_ollama(self, prompt: str) -> Optional[Dict]:
        try:
            result = subprocess.run(
                [self.ollama_path, "run", self.model_name],
                input=prompt.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120*2
            )
            stdout = result.stdout.decode().strip()
            stderr = result.stderr.decode().strip()
            print(f"STDOUT:\n{stdout}")
            print(f"STDERR:\n{stderr}")

            # Thử parse JSON từ code block
            json_match = re.search(r'```json\n(.*?)\n```', stdout, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Thử parse JSON trực tiếp
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                print(f"⚠️ Không thể parse JSON từ output:\n{stdout[:500]}...")
                return None

        except subprocess.TimeoutExpired:
            print("🕒 Timeout khi gọi Ollama")
            return None
        except Exception as e:
            print(f"❌ Lỗi khi gọi Ollama: {str(e)}")
            return None

    def generate_input_str(self, entry):
        """
        Chuẩn bị dữ liệu đầu vào từ entry
        
        Args:
            entry: Dict chứa thông tin địa điểm
            
        Returns:
            Chuỗi prompt được định dạng
        """
        location_parts = [
            entry.get("admin_level_3", ""),  # Cấp xã
            entry.get("admin_level_2", ""),  # Cấp huyện
            entry.get("admin_level_1", "")   # Cấp tỉnh
        ]
        location = ", ".join(filter(None, location_parts))

        # Tạo chuỗi input_str
        input_str = (
            f"Thông tin điểm đến:\n"
            f"- Tên: {entry.get('name', 'Không rõ')}\n"
            f"- Loại: {entry.get('category', 'địa điểm du lịch')}\n"
            f"- Vị trí: {location}\n"
            f"- Tọa độ: {entry.get('coordinates', [0, 0])}\n"
            f"- Mô tả: {entry.get('description', 'Không có mô tả')}\n"
            f"- URL hình ảnh: {entry.get('image_url', 'Không có URL hình ảnh')}\n"
        )

        # Trả về chuỗi đã được định dạng cho TOURISM_TEMPLATE
        return self.TOURISM_TEMPLATE.format(
            input_data=input_str,
            name=entry.get("name", "Không rõ"),
            address=location,
            category=entry.get("category", "địa điểm du lịch"),
            coordinates=entry.get("coordinates", [0, 0]),
            description=entry.get("description", "Không có mô tả"),
            image_url=entry.get("image_url", "Không có URL hình ảnh")
        )

    def process_single_entry(self, entry: Dict) -> Dict:
        """
        Xử lý một entry du lịch
        
        Args:
            entry: Dict chứa thông tin địa điểm
            
        Returns:
            Dict kết quả đã được xử lý
        """
        try:
            # Chuẩn bị prompt
            prompt = self.generate_input_str(entry)  # Sửa lại đây
            
            # Gọi Ollama
            response = self.call_ollama(prompt)
            
            if not response:
                return {
                    **entry,
                    "error": "Không nhận được phản hồi từ Ollama",
                    "processed": False
                }
                
            # Kiểm tra chất lượng description
            description = response.get("description", "")
            if len(description.split()) < 3:
                raise ValueError("Mô tả quá ngắn")
                
            return {
                **entry,
                **response,
                "processed": True
            }
            
        except Exception as e:
            return {
                **entry,
                "error": str(e),
                "processed": False
            }

    def process_batch(self, entries: List[Dict]) -> List[Dict]:
        """
        Xử lý một batch dữ liệu
        
        Args:
            entries: Danh sách các entry cần xử lý
            
        Returns:
            Danh sách kết quả đã xử lý
        """
        print(f"Xử lý {len(entries)} entries")
        with ThreadPoolExecutor() as executor:
            results = list(tqdm(
                executor.map(self.process_single_entry, entries),
                total=len(entries),
                desc="Đang xử lý các mục"
            ))
        return results

    def save_results(self, results, output_file):
        """
        Phương thức lưu kết quả vào file JSON
        
        Args:
            results: Dữ liệu cần lưu
            output_file: Đường dẫn file đầu ra
        """
        print(f"Kết quả trước khi lưu:\n{json.dumps(results, ensure_ascii=False, indent=2)}")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")

# Dữ liệu mẫu
sample_data = [
    {
        "name": "Xóm Mui",
        "category": "town",
        "coordinates": [104.7305, 8.6061],
        "admin_level_1": "Ca Mau",
        "admin_level_2": "Ngoc Hien District",
        "admin_level_3": "Vien An Dong"
    },
    {
        "name": "Mũi Cà Mau",
        "category": "tourist_spot",
        "coordinates": [104.7266, 8.6225],
        "admin_level_1": "Ca Mau",
        "admin_level_2": "Ngoc Hien District",
        "admin_level_3": "Dat Mui"
    }
]
print("Dữ liệu đầu vào:", json.dumps(sample_data, ensure_ascii=False, indent=2))
# Định nghĩa các biến cần thiết
OLLAMA_PATH = r"C:\Users\21520\AppData\Local\Programs\Ollama\ollama.exe"  # Thay bằng đường dẫn thực tế
MODEL_NAME = "mistral"  # Thay bằng tên model thực tế
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE = f"travel_{timestamp}.json"  # Đường dẫn file để lưu kết quả

# Khởi tạo processor
processor = OllamaTourismProcessor(OLLAMA_PATH, MODEL_NAME)

# Xử lý dữ liệu
results = processor.process_batch(sample_data)

# Lưu kết quả
processor.save_results(results, OUTPUT_FILE)
