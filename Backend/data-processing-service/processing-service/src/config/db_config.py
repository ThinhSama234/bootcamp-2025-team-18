from dotenv import load_dotenv
import os

load_dotenv()

TRAVELDB_URL = os.getenv("TRAVELDB_URL")

if not TRAVELDB_URL:
  raise Exception("TRAVELDB_URL is not set in environment variables")

DEFAULT_EMBEDDING_MODEL = "models/all-MiniLM-L6-v2-f16.gguf"