import json
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
from data_interface import MongoDB
def clean_address(address_text):
    """Clean and normalize the address string"""
    if not address_text:
        return None
    # Remove extra whitespace and normalize commas
    address_text = ' '.join(address_text.split())
    address_text = address_text.replace(' ,', ',').replace(',,', ',')
    return address_text.strip()

def extract_category_from_name(name):
    """Extract potential category from restaurant name"""
    if not name:
        return "restaurant"
    
    name_lower = name.lower()
    if 'cafe' in name_lower or 'coffee' in name_lower:
        return "cafe"
    elif 'hải sản' in name_lower or 'seafood' in name_lower:
        return "seafood"
    elif 'chay' in name_lower:
        return "vegetarian"
    elif 'steak' in name_lower or 'bò' in name_lower:
        return "steakhouse"
    elif 'lounge' in name_lower or 'bar' in name_lower:
        return "lounge"
    return "restaurant"

def extract_restaurant_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # Find all restaurant entries by looking for h2 tags followed by address divs
    restaurant_entries = []
    
    # First find all h2 tags that likely contain restaurant names
    h2_tags_name = soup.find_all('h2')
    div_tags_address = soup.find_all('div', class_ = "address")
    for h2, address2 in zip(h2_tags_name, div_tags_address):
        restaurant = {'name_tag': h2, "address_tag": address2}
        restaurant_entries.append(restaurant)
    
    for entry in restaurant_entries:
        restaurant_data = {
            "type": "location",
            "data": {
                "address": None,
                "district": None,
                "city": "TP. HCM",
                "latitude": None,
                "longitude": None,
                "category": "restaurant",
                "name": None,
                "url": None
            }
        }
        
        # Extract name and URL
        name_tag = entry['name_tag']
        a_tag = name_tag.find('a')
        if a_tag:
            restaurant_data["data"]["name"] = a_tag.get('title', '').strip() or a_tag.text.strip()
            restaurant_data["data"]["url"] = a_tag.get('href', '')
        
        # Extract address components
        address_tag = entry['address_tag']
        if address_tag:
            address_parts = []
            district = None
            
            # Get all text elements
            for span in address_tag.find_all('span'):
                text = span.text.strip()
                if text and text != "TP. HCM":
                    address_parts.append(text)
            
            # Extract district from <a> tag if exists
            a_tag = address_tag.find('a')
            if a_tag:
                district = a_tag.text.strip()
                restaurant_data["data"]["district"] = district
            
            # Combine address parts
            full_address = ', '.join(address_parts)
            restaurant_data["data"]["address"] = clean_address(full_address)
        
        # Determine category from name
        if restaurant_data["data"]["name"]:
            restaurant_data["data"]["category"] = extract_category_from_name(restaurant_data["data"]["name"])
        
        # Only add if we have at least a name
        if restaurant_data["data"]["name"]:
            results.append(restaurant_data)
    
    return json.dumps(results, indent=2, ensure_ascii=False, sort_keys=False)

def save_to_json(data, filename='restaurants.json'):
    """Save extracted data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved data to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return False
    
def save_to_mongodb(data_json, URL = "TRAVELDB_URL", db_name = "travel_db", collection_name="locations"):
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

result = {
    "type": "location",
    "data": {
        "name": "Ngã ba Đồng Lộc",
        "address": "Xã Đồng Lộc, huyện Can Lộc, tỉnh Hà Tĩnh",
        "description": "Vị trí ngã ba Đồng Lộc là giao điểm của quốc lộ 15A và tỉnh lộ 2 (Hà Tĩnh). Trong những năm tháng kháng chiến chống Mỹ, mọi con đường chi viện từ Bắc vào Nam đều phải đi qua nơi đây. Chính vì sự hiểm yếu này mà không quân Mỹ đã liên tục cho máy bay ném bom đánh phá Đồng Lộc nhằm mục đích cắt đứt huyết mạch giao thông của quân dân ta hướng về miền Nam. Vì thế, Đồng Lộc còn được mệnh danh là “tọa độ chết” khi mỗi m2 nơi đây đều phải gánh tới 3 quả bom tấn. Để bảo vệ con đường huyết mạch này, 10 cô gái thanh niên xung phong đã anh dũng hy sinh trong khi làm nhiệm vụ. Họ đã trở thành biểu tượng của tinh thần yêu nước, lòng dũng cảm và sự hy sinh cao cả của thế hệ trẻ Việt Nam trong cuộc kháng chiến chống Mỹ cứu nước. Ngã ba Đồng Lộc đã được Nhà nước phong tặng danh hiệu Anh hùng lực lượng vũ trang nhân dân và được công nhận là di tích lịch sử cấp quốc gia đặc biệt.",
        "latitude": "11.335",
        "longitude": "107.355",
        "category": "di tích lịch sử",
        "image_url": ["https://statics.vinpearl.com/nga-ba-dong-loc-3_1629474212.jpg", "https://statics.vinpearl.com/nga-ba-dong-loc-7_1629474329.jpg", "https://statics.vinpearl.com/nga-ba-dong-loc-8_1629474349.jpg"],
    }
}

save_to_mongodb(result)