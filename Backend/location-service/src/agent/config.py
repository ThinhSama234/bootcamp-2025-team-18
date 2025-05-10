from pathlib import Path

import os

PROJECT_ROOT = Path(__file__).parent

DATA_DIR = PROJECT_ROOT / "data"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
DEFAULT_EMBEDDING_MODEL = "models/all-MiniLM-L6-v2-f16.gguf"