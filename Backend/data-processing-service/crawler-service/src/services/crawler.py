import json
import requests
import time
import logging
import json
import re
import os
import logging
from typing import Dict, Any, List, Optional
import requests
from requests.adapters import HTTPAdapter
from ratelimit import limits, sleep_and_retry
from urllib3.util.retry import Retry
from dataclasses import dataclass
from dotenv import load_dotenv

from bs4 import BeautifulSoup
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from google import genai

from models.location import Location

logger = logging.getLogger(__name__)

load_dotenv()

GENAI_API_KEY = os.getenv('GENAI_API_KEY')
if not GENAI_API_KEY:
  raise EnvironmentError('Missing GEN_API_KEY env')

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

@dataclass
class CrawlerConfig:
  """Configuration for the crawler"""
  max_retries: int = 3
  retry_backoff_factor: float = 0.5
  timeout: int = 10
  max_workers: int = 5
  calls_per_minute: int = 30  # Rate limiting
  user_agent: str = USER_AGENT

class Crawler:
  def __init__(self, config: Optional[CrawlerConfig] = None):
    self.config = config or CrawlerConfig()
    self.session = self._setup_session()
    self.processed_urls = set()
    self.client = genai.Client(api_key=GENAI_API_KEY)
    
  def _setup_session(self) -> requests.Session:
    """Configure requests session with retries and timeouts"""
    session = requests.Session()
    retry_strategy = Retry(
      total=self.config.max_retries,
      backoff_factor=self.config.retry_backoff_factor,
      status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": self.config.user_agent})
    return session

  def close(self):
    """Clean up resources"""
    self.session.close()

  @sleep_and_retry
  @limits(calls=CrawlerConfig.calls_per_minute, period=60)
  def _fetch_page(self, url: str) -> Optional[str]:
    """
    Fetch a page with rate limiting and retries
    """
    try:
      response = self.session.get(url, timeout=self.config.timeout)
      response.raise_for_status()
      return response.text
    except requests.RequestException as e:
      logger.error(f"Error fetching {url}: {str(e)}")
      return None

  def crawl_location_paper_urls(self, province_url) -> List[str]:
    html = self._fetch_page(province_url)
    soup = BeautifulSoup(html, "html.parser")
    
    attraction_sections = soup.find("h2", string="Điểm tham quan nổi tiếng")
    if not attraction_sections:
      logger.info("'Điểm tham quan nổi tiếng' not found on province page.")
      return

    see_all_link = attraction_sections.find_next("a", class_="see-all")
    if not see_all_link:
      logger.info("'see-all' not found on 'Điểm tham quan nổi tiếng'.")
      return
    
    base_url = "https://mia.vn"
    all_attractions_url = base_url +"/"+ see_all_link["href"]
    logger.info(f"Location urls: {all_attractions_url}")
    
    result_urls = []
    page = 1
    while True:
      page_url = all_attractions_url if page == 1 else f"{all_attractions_url.split('?')[0]}?page={page}"
      page_html = self._fetch_page(page_url)
      soup = BeautifulSoup(page_html, "html.parser")
      
      attraction_cards = soup.find_all(class_="article-link")
      if not attraction_cards:
        logger.info(f"No locations found on page '{page}'. Stopped.")
        break
      if not attraction_cards:
        logger.info(f"No locations found on page '{page}'.")
        break
      count = 0
      for card in attraction_cards:
        link = card["href"]
        paper_url = base_url + "/" + link
        result_urls.append(paper_url)
        count += 1
      logger.info(f"Found {count} locations on page '{page}'")
      
      page += 1
      time.sleep(1)
      
    return result_urls

  def _extract_json(self, message: AIMessage) -> List[dict]:
    """Extracts JSON content from a string where JSON is embedded between ```json``` tags.

    Parameters:
        message (AIMessage): The message containing the JSON content.

    Returns:
        list: A list of extracted JSON strings.
    """
    text: str = message.content
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```json(.*?)```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
      return [json.loads(match.strip()) for match in matches]
    except Exception:
      raise ValueError(f"Failed to parse: {message}")
      
  def _align_text(self, text):
    """Aligns a messy text into a structured, readable format."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    aligned_text = []
    current_section = None
    current_subsection = None
    in_list = False
    
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
        key, value = map(str.strip, line.split(':', 1))
        if key.lower() in ["địa chỉ", "giờ mở cửa", "giá vé"]:
          aligned_text.append(f"- **{key.capitalize()}**: {value}")
          continue
      
      # Nếu không phải tiêu đề, không phải danh sách, thì là đoạn văn
      in_list = False

      line = re.sub(r'\bMIA\.vn\b', '', line, flags=re.IGNORECASE)
      line = line.strip()
      if line:
        aligned_text.append(f"{line}")
  
    return '\n'.join(aligned_text).strip()

  def _parse_html_to_text_and_images(self, html_content):
    """Parse HTML to extract text and image URLs."""
    html_str = str(html_content)
    image_urls = re.findall(r'<img [^>]*src="([^"]+)"', html_str)

    html_content = html_content.get_text(separator="\n", strip=True)
    after_align = self._align_text(html_content)
    
    return after_align, image_urls

  def _prompt_ai_for_model(self, query, image_urls):
    prompt = ChatPromptTemplate.from_messages([
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
        f"Use the provided image_urls: {image_urls} for the 'image_url' field in the JSON output. "
        "If any information (like latitude, longitude) is missing, use "". "
        "Make sure to wrap the answer in ```json``` tags",
      ),
      ("human", f"{query}"),
    ]).partial(schema=Location.model_json_schema(), image_urls=image_urls)
    # Chuẩn bị nội dung prompt để gửi đến Gemini
    formatted_prompt = prompt.format_prompt(query=query).to_string()
    # Gửi yêu cầu đến Gemini và nhận phản hồi
    response = self.client.models.generate_content(
      model="gemini-2.0-flash",
      contents=formatted_prompt
    )
    
    # Trích xuất JSON từ phản hồi
    result = self._extract_json(AIMessage(content=response.text)) 
    
    if not result or not isinstance(result, list) or len(result) == 0:
        raise ValueError("Invalid JSON response")
    
    return Location(**result[0])

  def crawl_location(self, paper_url: str, max_tries=3, delay=2) -> Dict[str, Any]:
    if paper_url in self.processed_urls:
      return None

    location_data = None
    for attempt in range(max_tries):
      try:
        logger.info(f"Attempt {attempt + 1} to process URL: {paper_url}")

        html_content = self._fetch_page(paper_url)
        soup = BeautifulSoup(html_content, "html.parser")

        main_content = soup.find("div", class_="post-content")
        query, image_urls = self._parse_html_to_text_and_images(main_content)

        location = self._prompt_ai_for_model(query, image_urls)
        location_data = {
          'type': location.type,
          'data': location.data.model_dump()
        }
        break
      except (ValueError, Exception) as e:
        logger.error(f"Error processing '{paper_url}' ({attempt + 1}/{max_tries}) tries: {e}")
        if attempt == max_tries - 1:
          logger.error(f"Can not process {paper_url} after {max_tries} attempts")
          return
        time.sleep(delay)
    
    if location_data:
      self.processed_urls.add(paper_url)
    return location_data
