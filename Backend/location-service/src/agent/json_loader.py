import json
from pathlib import Path
import os

def load_json_data(data_dir: Path, json_files: list) -> list:
    """
    Load JSON files and extract relevant fields into merged text.
    """

    merged_texts = []
    
    for json_file in json_files:
        file_path = data_dir / json_file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                destinations = json.load(f)

            for dest in destinations:
                data = dest.get('data', {})
                name = data.get('name', '')
                address = data.get('address', '')
                description = data.get('description', '')
                merged_text = f"{name} {address} {description}"
                merged_texts.append(merged_text)
                print(f"✅ Loaded data for {name} from {json_file}")
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")

    return merged_texts