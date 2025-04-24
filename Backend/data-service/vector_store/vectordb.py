from typing import Optional
from langchain.embeddings.base import Embeddings

from config import DATA_DIR, VECTOR_DB_DIR, DEFAULT_EMBEDDING_MODEL

class vectorDB:
    def __init__(self, embedding_model: Optional[Embeddings] = None, data_dir = DATA_DIR, vector_db_dir = VECTOR_DB_DIR):

        pass