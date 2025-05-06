import requests
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
from data_interface import MongoDB 
from dotenv import load_dotenv
def extract_wiki_content_by_title(title: str) -> str | None:
    """Truy cập trực tiếp và trích xuất nội dung từ trang Wikipedia tiếng Việt."""
    # Encode tiêu đề để đảm bảo URL hợp lệ
    encoded_title = quote(title.replace(" ", "_"))
    url = f"https://vi.wikipedia.org/wiki/{encoded_title}"

    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print(f"❌ Không truy cập được URL: {url}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    paragraphs = soup.select("p")
    content = "\n".join(
        p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
    )
    return content

def extract_vietnamtourism_content_by_title(dest = "dest", item:int = 1, isItem=1)->str|None: #https://csdl.vietnamtourism.gov.vn/dest/?page=65
    if isItem:
        url = f"https://csdl.vietnamtourism.gov.vn/{dest}/?item={item}"
        print(url)
    else:
        url = "https://csdl.vietnamtourism.gov.vn/{dest}/?page=65"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print(f"❌ Không truy cập được URL: {url}")
        return None
    content = {}
    soup = BeautifulSoup(res.text, "html.parser")
    if isItem:
        title_tag = soup.find('h4')
        if title_tag:
            link_tag = title_tag.find('a')
            if link_tag:
                title = link_tag.text.strip()
            address_tag = soup.find_all('span', class_='d-block')
            if address_tag:
                address = address_tag[1].text.strip().replace('Địa chỉ: , ', '')
                address = address_tag[1].text.strip().replace('Địa chỉ:', '')
            paragraphs = soup.select("p")
            discription = "\n".join(
                p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
            )
            items = soup.find_all('div', class_ = 'item text-center')
            image_links = None
            if items:
                image_links = [item.find('a')['href'] for item in items if item.find('a', href=True)]
                for link in image_links:
                    print(link)
            print("Title:", title)
            print("discription:", discription)
            print("Address:", address)
            content = {
                "name": title,
                "address": address,
                "discription": discription,
                "image_url": image_links
            }
    else:
        # Extract the information
        title_tag = soup.find('h4').find('a')
        title = title_tag.text.strip()
        link = title_tag['href'].strip()

        address_tag = soup.find('span', class_='d-block')
        address = address_tag.text.strip().replace('Địa chỉ: , ', '')

        # Print the results
        print("Title:", title)
        print("Link:", link)
        print("Address:", address)
        content = {
            "Title:", title,
            "Address:", address
        }
    return content
if __name__ == "__main__":
    load_dotenv()
    DB_URL = os.getenv("vietnamtourism_URL")
    if not DB_URL:
        raise Exception("TRAVELDB_URL is not set in environment variables") 
    print("MongoDB URL:", DB_URL) 
    db = MongoDB(DB_URL, "vietnamtourism_db", "restaurant")
    for i in range(1, 14480):
        content = extract_vietnamtourism_content_by_title(dest = "cslt", item = i, isItem=1)
        if content == None or content == {}:
            continue
        db.save_record({
            "type": "service",
            "data": content,
        })
    print("Số lượng documents hiện tại:", db.count_documents({}))
    print(db.list_collections()) 
    db.close()
    print("MongoDB connection closed.")
    #es = Elasticsearch(["http://localhost:9200"])
    # with open("location_name.txt", "r", encoding="utf-8") as f:
    #     lines = f.readlines()
    # for line in lines:
    #     location_name = line.strip()  # .strip() để bỏ ký tự xuống dòng \n
    #     print(f"📍 Địa điểm: {location_name}")
    #     query = location_name
    #     print(f"📘 Đang truy xuất Wikipedia cho: {query}")
    #     content = extract_wiki_content_by_title(query)
    #     if content:
    #         print(f"📄 Nội dung trích xuất (500 ký tự đầu):\n{content[:3000]}")
    #         es_document = {
    #             "wiki_content": content,
    #             "_id": query,
    #             "last_updated": datetime.now().strftime("v%Y%m%d_%H%M%S")
    #         }
    #     # es.index(index="landmark_content", id=query, body=es_document)
    #     # metadata = {
    #     # "name": "Nhà Thờ Lớn Hà Nội",
    #     # "location": "Hà Nội, Việt Nam",
    #     # "year_built": 1886,
    #     # "category": "Church"
    #     # }
    #     # mongo_document = {
    #     # "_id": query,
    #     # "metadata": metadata,
    #     # "content_id": query,
    #     # "last_updated": datetime.now().strftime("v%Y%m%d_%H%M%S")
    #     # }
    #         db.save_record(es_document)
    #     else:
    #         print("❌ Không tìm thấy nội dung.")
    # print("Số lượng documents hiện tại:", db.count_documents({}))
    # db.close()
    # print("MongoDB connection closed.")
