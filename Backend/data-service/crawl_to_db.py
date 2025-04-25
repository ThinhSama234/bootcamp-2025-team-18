import json
from bs4 import BeautifulSoup

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

# Example usage:
html_content = html_content
restaurant_json = extract_restaurant_data(html_content)
print(restaurant_json)
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
if restaurant_json:
    save_to_json(restaurant_json)
    print(f"Extracted {len(restaurant_json)} restaurants")
else:
    print("No restaurants found in the HTML content")