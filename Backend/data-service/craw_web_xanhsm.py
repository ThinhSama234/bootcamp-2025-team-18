from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain.chat_models import init_chat_model
import json
import re
import os
import sys
import logging
import requests
from bs4 import BeautifulSoup
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../crawl_data/Data")))
from dotenv import load_dotenv
# model = init_chat_model("gpt-4o-mini", model_provider="openai")
from google import genai
from data_interface import MongoDB
import cloudscraper
# Cấu hình API key cho Google Generative AI (thay bằng API key của bạn)

# Khởi tạo client và mô hình Gemini
client = genai.Client(api_key="AIzaSyDU3Hl2kTKLMOPJlK4tIU3s6vpHYq8d-58")

class LocationData(BaseModel):
    """ Location data model """
    name : str = Field(..., description="Tên của địa điểm")
    address : str = Field(..., description="Địa chỉ của địa điểm")
    description : str = Field(..., description="Mô tả về địa điểm")
    category: str = Field(default="", description="Phân loại địa điểm với định dạng (nếu không có thì thôi): '[sao] [giá thành] [loại sở hữu] [loại hình] [văn hóa]', ví dụ: '4.5 sao, giá cao, thiên nhiên, khu du lịch, tâm linh'")
    latitude : str = Field(default="", description="Vĩ độ của địa điểm")
    longitude : str = Field(default="", description="Kinh độ của địa điểm")
    image_url : List[str] = Field(default=[], description="URL của hình ảnh địa điểm")
class Location(BaseModel):
    """ Location model """
    type: str = Field(..., description="Loại đối tượng, ví dụ: 'Location', 'Restaurant', 'Hotel'")
    data: LocationData = Field(..., description="Thông tin chi tiết của địa điểm")
def extract_json(message: AIMessage) -> List[dict]:
    """Extracts JSON content from a string where JSON is embedded between ```json``` tags.

    Parameters:
        message (AIMessage): The message containing the JSON content.

    Returns:
        list: A list of extracted JSON strings.
    """
    text = message.content
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```json(.*?)```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
        return [json.loads(match.strip()) for match in matches]
    except Exception:
        raise ValueError(f"Failed to parse: {message}")
    
def save_json_to_file(json_data, file_path):
    """Saves JSON data to a file."""
    # không tồn tại thì tạo mới
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    # ghi đè nếu tồn tại
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    # In đường dẫn tuyệt đối
    print("File saved at:", os.path.abspath(file_path))
def load_json_from_file(file_path):
    """Loads JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def align_text(text):
    """Aligns a messy text into a structured, readable format."""
    # Loại bỏ khoảng trắng thừa và chuẩn hóa dòng
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Khởi tạo biến để lưu văn bản đã căn chỉnh
    aligned_text = []
    current_section = None
    current_subsection = None
    in_list = False
    
    # Xử lý từng dòng
    for line in lines:
        # Kiểm tra tiêu đề chính (1, 2, 3,...)
        if re.match(r'^\d+\s*$', line):
            current_section = int(line)
            aligned_text.append(f"\n### {current_section}. ")
            continue
            
        # Kiểm tra tiêu đề phụ (3.1, 3.2,...)
        if re.match(r'^\d+\.\d+\s+.*$', line):
            current_subsection = line.strip()
            aligned_text.append(f"\n#### {current_subsection}")
            continue
            
        # Kiểm tra các mục dạng liệt kê (bắt đầu bằng '-')
        if line.startswith('-'):
            in_list = True
            aligned_text.append(f"- {line[1:].strip()}")
            continue
            
        # Kiểm tra các thông tin cụ thể như địa chỉ, giờ mở cửa, giá vé
        if ':' in line and not in_list:
            # Chia thành key-value
            key, value = map(str.strip, line.split(':', 1))
            if key.lower() in ["địa chỉ", "giờ mở cửa", "giá vé"]:
                aligned_text.append(f"- **{key.capitalize()}**: {value}")
                continue
        
        # Nếu không phải tiêu đề, không phải danh sách, thì là đoạn văn
        in_list = False
        # Loại bỏ các cụm từ không cần thiết (ví dụ: MIA.vn)
        line = re.sub(r'\bMIA\.vn\b', '', line, flags=re.IGNORECASE)
        line = line.strip()
        if line:
            aligned_text.append(f"{line}")
    
    # Kết hợp các dòng thành văn bản hoàn chỉnh
    return '\n'.join(aligned_text).strip()

def parse_html_to_text_and_images(html_content):
    """Parse HTML to extract text and image URLs."""
    # Trích xuất URL ảnh từ thẻ <img>
    html_str = str(html_content)
    image_urls = re.findall(r'<img [^>]*src="([^"]+)"', html_str)
    # copy html_content để xử lý
    html_content = html_content.get_text(separator="\n", strip=True)
    after_align = align_text(html_content)
    
    return after_align, image_urls

def save_to_mongodb(data_json, URL = "TRAVELDB_URL", db_name = "travel_db", collection_name="new_locations"):
    """Saves data to MongoDB."""
    load_dotenv()
    DB_URL = os.getenv(URL)
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")
    """Saves data to MongoDB."""
    # Kết nối đến MongoDB
    db = MongoDB(DB_URL, db_name, collection_name)
    db.save_record(data_json)
    print("Data saved to MongoDB successfully.")
    print("Số lượng doc hiện tại là:",db.count_documents()) 
    db.close()
    return

def save_to_mongodb_full_text(name, full_text, URL = "TRAVELDB_URL", db_name = "travel_db", collection_name="more_details"):
    """Saves data to MongoDB full text."""
    load_dotenv()
    DB_URL = os.getenv(URL)
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")
    # Kết nối đến MongoDB
    db = MongoDB(DB_URL, db_name, collection_name)
    db.save_record(
        {
            'type': 'full_text',
            'name': name,
            'full_text': full_text,
            "ref_id": "",
        }
    )
    print("Data saved to MongoDB successfully.")
    print("Số lượng doc hiện tại là:",db.count_documents())
    db.close()
    return

def xanh_sm(file_path):
    """Main function to process URLs."""
    # Đọc file chứa các URL
    merge_texts = []
    images = []
    with open(file_path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    # Xử lý từng URL
    for url in urls:
        logging.info(f"Xử lý URL: {url}")
        headers = {"User-Agent": "Mozilla/5.0"}
        html_content = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html_content, "html.parser")
        main_content = soup.find("div", class_="content-wrapper read-more")
        # Trích xuất text từ thẻ p
        paragraph_text = soup.find('p').get_text()
        location = soup.find('ul', class_='wp-block-list').find('li').get_text().replace("Địa chỉ: ", "")
        image = soup.find_all('img')
        # có đuôi là .jpg, .png, .jpeg
        image = [img['src'] for img in image if img['src'].endswith(('.jpg'))]
        # lấy 2 thằng cuối image
        transport_list = soup.find_all('ul', class_='wp-block-list')[1].find_all('li')
        text = soup.find_all('p')
        view_more_index = -1
        for i, p in enumerate(text):
            if "Xem thêm:" in p.get_text():
                view_more_index = i
                break
        if view_more_index != -1:
            descriptions = text[:view_more_index]
        else:
            descriptions = text
        # merge all text I need
        merge_text = ""
        # Tạo description từ các đoạn văn trước "Xem thêm:"
        description = " ".join(p.get_text() for p in descriptions)
        
        merge_text += paragraph_text + "\n"
        merge_text += location + "\n"
        
        for transport in transport_list:
            #print(transport.get_text())
            merge_text += transport.get_text() + "\n"
        
        #print(description)
        
        merge_text += description
        print("====================================")
        print(merge_text)
        merge_texts.append(merge_text)
        images.append(image)
    return merge_texts, images

query, image_urls = xanh_sm("mia.txt")
qu, im = xanh_sm("mia.txt")
print("200 OK")
for query, image_urls in zip(qu, im):
    # Prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            (
            # "system",
            # "Answer the user query. Output your answer as JSON that "
            # "matches the given schema: ```json\n{schema}\n```."
            # "Make sure to wrap the answer in ```json``` tags",
            "system",
                "Extract location information from the user query and output it as JSON that matches the given schema: ```json\n{schema}\n```. "
                "Create a description as a concise sumary (4-5 sentences) with objective information: focus on the location's standout features, ecosystem, notable experiences, and reasons to choose it (e.g., natural beauty, unique activities, accessibility)."
                "Avoid subjective phrases (e.g., 'wonderful', 'amazing') and promotional content (e.g., 'MIA.vn', 'will bring you great experiences'). "
                "language will be Vietnamese. "
                "Determine the category based on the context using the following format: '[sao] [giá thành] [loại sở hữu] [loại hình] [văn hóa]', where: "
                "- [sao]: Số sao (ví dụ: 4.5 sao) nếu có thông tin đánh giá, bỏ qua nếu không có. "
                "- [giá thành]: 'giá cao' hoặc 'giá thấp' nếu có thông tin về chi phí, bỏ qua nếu không có. "
                "- [loại sở hữu]: 'thiên nhiên' hoặc 'tư nhân' dựa trên bối cảnh, bỏ qua nếu không rõ. "
                "- [loại hình]: Một trong 'khu du lịch', 'bảo tàng', 'di tích', 'biển', 'hồ', 'lăng', v.v., dựa trên mô tả, bỏ qua nếu không rõ. "
                "- [văn hóa]: Thêm 'tâm linh', 'thủ công', hoặc 'di sản văn hóa' nếu có yếu tố văn hóa liên quan, bỏ qua nếu không có. "
                "Use the provided image_urls: {image_urls} for the 'image_url' field in the JSON output. "
                "If any information (like latitude, longitude) is missing, use "". "
                "Make sure to wrap the answer in ```json``` tags",
            ),
            ("human", "{query}"),
        ]
    ).partial(schema=Location.model_json_schema(), image_urls=image_urls)

    #print("====================")
    #print("Extracted text:", query)
    #print("Extracted image URLs:", image_urls)
    print("====================================")
    #print(prompt.format_prompt(query=query).to_string())
    # Chuẩn bị nội dung prompt để gửi đến Gemini
    formatted_prompt = prompt.format_prompt(query=query).to_string()
    # Gửi yêu cầu đến Gemini và nhận phản hồi
    response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=formatted_prompt
            )
    # Trích xuất JSON từ phản hồi
    result = extract_json(AIMessage(content=response.text)) 
    print(result)
    #Lưu kết quả vào file JSON
    #save_json_to_file(result, "output3.json")
    # Lưu vào mongodb
    save_to_mongodb(result[0])
    save_to_mongodb_full_text(result[0]['data']['name'], query)
