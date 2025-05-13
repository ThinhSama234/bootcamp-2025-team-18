
from dotenv import load_dotenv
import os

load_dotenv()

TRAVELDB_URL = os.getenv("TRAVELDB_URL")
if not TRAVELDB_URL:
    raise Exception("TRAVELDB_URL is not set in environment variables")

DEFAULT_EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2.gguf2.f16.gguf"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY is not set in environment variables")

XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    raise Exception("XAI_API_KEY is not set in environment variables")