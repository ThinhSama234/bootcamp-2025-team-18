import os
import json
from datetime import datetime
from typing import Dict

VERSION_LOG_FILE = "faiss_index_version.json"

def get_version_timestamp() -> str:
    return datetime.now().strftime("v%Y%m%d_%H%M%S")

def load_version_log() -> Dict:
    if not os.path.exists(VERSION_LOG_FILE):
        return {}
    with open(VERSION_LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_version_log(log: Dict):
    with open(VERSION_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)