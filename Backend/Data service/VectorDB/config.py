from pathlib import Path
import os

# Thư mục gốc
PROJECT_ROOT = Path(__file__).parent

# Cấu hình đường dẫn
DATA_DIR = PROJECT_ROOT / "data"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
DEFAULT_EMBEDDING_MODEL = "models/all-MiniLM-L6-v2-f16.gguf"