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
from dotenv import load_dotenv
import time
# model = init_chat_model("gpt-4o-mini", model_provider="openai")
from google import genai
from data_interface import MongoDB
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

def save_to_mongodb(data_json, query, URL = "TRAVELDB_URL", db_name = "travel_db", collection_name="auto_crawl"):
    """Saves data to MongoDB."""
    load_dotenv()
    DB_URL = os.getenv(URL)
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables")
    """Saves data to MongoDB."""
    # Kết nối đến MongoDB
    db = MongoDB(DB_URL, db_name, collection_name)
    record_id, error = db.save_record(data_json)
    save_to_mongodb_full_text(data_json['data']['name'], query, ref_id = record_id, URL=URL, db_name=db_name, collection_name=collection_name)
    print("Data saved to MongoDB successfully.")
    print("Số lượng doc hiện tại là:",db.count_documents())
    return

def save_to_mongodb_full_text(name, full_text, ref_id, URL = "TRAVELDB_URL", db_name = "travel_db", collection_name="auto_crawl_text"):
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
            "ref_id": ref_id,
        }
    )
    print("Data saved to MongoDB successfully.")
    print("Số lượng doc hiện tại là:",db.count_documents())
    return
def process_url(url, max_retries=3, delay=2):
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempt {attempt + 1} to process URL: {url}")
            html_content = requests.get(url, headers=headers).text
            soup = BeautifulSoup(html_content, "html.parser")
            main_content = soup.find("div", class_="post-content")
            print("200 OK")
            query, image_urls = parse_html_to_text_and_images(main_content)
            # Prompt
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
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
            # kiem tra json co hop le khong
            if not result or not isinstance(result, list) or len(result) == 0:
                raise ValueError("Invalid JSON response")
            Location(**result[0])
            print(result)
            # Lưu vào mongodb
            save_to_mongodb(result[0], query)
            return
        except (ValueError, Exception) as e:
            logging.error(f"Lỗi khi xử lý URL {url} (Thử lần {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                logging.error(f"Không thể xử lý URL {url} đã thử hết nhưng vẫn thất bại.")
                return
            time.sleep(delay)  # Delay before retrying
#url = "https://mia.vn/cam-nang-du-lich/vuon-trai-cay-cai-mon-toa-do-giai-nhiet-ngay-nang-nong-11062"
with open("attraction_links.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]
for url in urls:
    process_url(url, max_retries=3, delay=2)












# chain = prompt | model | extract_json
# result = chain.invoke({"query": query})
# print(result)

# #restaurant_json = extract_restaurant_data(html_content)
# #print(restaurant_json)
# from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
# from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain_experimental.tabular_synthetic_data.openai import (
#     OPENAI_TEMPLATE,
#     create_openai_data_generator,
# )
# from langchain_experimental.tabular_synthetic_data.prompt import (

# )
# from langchain_openai import ChatOpenAI

# #%%capture
# #!pip install -U langchain langchain_experimental openai

# # import os
# # os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
# class MedicalBilling(BaseModel):
#     patient_id: int
#     patient_name: str
#     diagnosis_code: str
#     procedure_code: str
#     total_charge: float
#     insurance_claim_amount: float

# examples = [
#     {"example": """Patient ID: 123456, Patient Name: John Doe, Diagnosis Code: J20.9, Procedure Code: 99203, Total Charge: $500, Insurance Claim Amount: $350"""},
#     {"example": """Patient ID: 789012, Patient Name: Johnson Smith, Diagnosis Code: M54.5, Procedure Code: 99213, Total Charge: $150, Insurance Claim Amount: $120"""},
#     {"example": """Patient ID: 345678, Patient Name: Emily Stone, Diagnosis Code: E11.9, Procedure Code: 99214, Total Charge: $300, Insurance Claim Amount: $250"""},
# ]
# OPENAI_TEMPLATE = PromptTemplate(
#     template="Generate a medical billing record for the following patient: {example}",
#     input_variables=["example"],
#     output_parser=MedicalBilling,
# )

# #OPENAI_TEMPLATE = PromptTemplate(input_variables=["example"], template="{example}")

# prompt_template = FewShotPromptTemplate(
#     prefix = SYNTHETIC_DATA_PREFIX,
#     examples = examples,
#     suffix = SYNTHETIC_DATA_SUFFIX,
#     input_variables=["subject", "extra"],
#     example_prompt=OPENAI_TEMPLATE,
# )

# synthetic_data_generator = create_openai_data_generator(
#     output_schema=MedicalBilling,
#     llm=ChatOpenAI(temperature=1),
#     prompt=prompt_template,
# )

# synthetic_results = synthetic_data_generator.generate(
#     subject="medical_billing",
#     extra="the name must be chosen at random. Make it something you wouldn't normally choose.",
#     runs=10,
# )

# from typing import List, Optional

# from langchain_core.output_parsers import PydanticOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from pydantic import BaseModel, Field, validator


# class Person(BaseModel):
#     """Information about a person."""

#     name: str = Field(..., description="The name of the person")
#     height_in_meters: float = Field(
#         ..., description="The height of the person expressed in meters."
#     )


# class People(BaseModel):
#     """Identifying information about all people in a text."""

#     people: List[Person]


# # Set up a parser
# parser = PydanticOutputParser(pydantic_object=People)

# # Prompt
# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "Answer the user query. Wrap the output in `json` tags\n{format_instructions}",
#         ),
#         ("human", "{query}"),
#     ]
# ).partial(format_instructions=parser.get_format_instructions())

# import json
# import re
# from typing import List, Optional

# from langchain_anthropic.chat_models import ChatAnthropic
# from langchain_core.messages import AIMessage
# from langchain_core.prompts import ChatPromptTemplate
# from pydantic import BaseModel, Field, validator


# class Person(BaseModel):
#     """Information about a person."""

#     name: str = Field(..., description="The name of the person")
#     height_in_meters: float = Field(
#         ..., description="The height of the person expressed in meters."
#     )


# class People(BaseModel):
#     """Identifying information about all people in a text."""

#     people: List[Person]


# # Prompt
# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "Answer the user query. Output your answer as JSON that  "
#             "matches the given schema: \`\`\`json\n{schema}\n\`\`\`. "
#             "Make sure to wrap the answer in \`\`\`json and \`\`\` tags",
#         ),
#         ("human", "{query}"),
#     ]
# ).partial(schema=People.schema())


# # Custom parser
# def extract_json(message: AIMessage) -> List[dict]:
#     """Extracts JSON content from a string where JSON is embedded between \`\`\`json and \`\`\` tags.

#     Parameters:
#         text (str): The text containing the JSON content.

#     Returns:
#         list: A list of extracted JSON strings.
#     """
#     text = message.content
#     # Define the regular expression pattern to match JSON blocks
#     pattern = r"\`\`\`json(.*?)\`\`\`"

#     # Find all non-overlapping matches of the pattern in the string
#     matches = re.findall(pattern, text, re.DOTALL)

#     # Return the list of matched JSON strings, stripping any leading or trailing whitespace
#     try:
#         return [json.loads(match.strip()) for match in matches]
#     except Exception:
#         raise ValueError(f"Failed to parse: {message}")