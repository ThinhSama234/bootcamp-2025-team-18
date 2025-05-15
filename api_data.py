import json
import concurrent.futures
import requests
import ijson

SERVER_URL = 'http://144.126.240.234:8000'
BATCH_SIZE = 1000
MAX_WORKERS = 5

def call_import_api(endpoint, data):
    url = f"{SERVER_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def process_batch(i, chunk):
    print(f"Processing batch {i} with {len(chunk)} items")
    batch = [{
        'topic': 'location-bigdata',
        'source': 'travel_locations',
        'type': 'Location',
        'data': {
            'name': loc.get('name', 'unknown'),
            'description': loc.get('description', ''),
            'address': loc.get('address', ''),
            'category': loc.get('category', ''),
            'latitude': loc.get('latitude', ''),
            'longitude': loc.get('longitude', ''),
            'image_url': loc.get('image_url', []),
        }
    } for loc in chunk]
    
    response = call_import_api('api/v1/import/batch', {'items': batch})
    
    if response and response.get('status') == 'success':
        print(f"Batch {i+1} imported successfully.")
        return True
    else:
        print(f"Batch {i+1} import failed: {response.get('message', 'Unknown error') if response else 'No response'}")
        return False

def stream_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        parser = ijson.items(f, 'item')  # Giả sử JSON là mảng, đọc từng "item"
        batch = []
        batch_count = 0
        for item in parser:
            batch.append(item)
            if len(batch) >= BATCH_SIZE:
                yield batch_count, batch
                batch = []
                batch_count += 1
        if batch:  # Xử lý lô cuối nếu còn dữ liệu
            yield batch_count, batch

print(f"Processing travel locations with {MAX_WORKERS} threads")

successful_batches = 0
failed_batches = 0
it = 2
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = []
    for i, chunk in stream_json_file('files/travel_locations.json'):
        future = executor.submit(process_batch, i, chunk)
        futures.append(future)
        if it < 0:
            break
        it -= 1
    for future in concurrent.futures.as_completed(futures):
        if future.result():
            successful_batches += 1
        else:
            failed_batches += 1

nchunks = successful_batches + failed_batches
print(f"\nImport summary:")
print(f"- Successfully imported batches: {successful_batches}")
print(f"- Failed batches: {failed_batches}")
print(f"- Success rate: {successful_batches/nchunks*100:.1f}%" if nchunks > 0 else "- Success rate: N/A")