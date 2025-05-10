import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import numpy as np
from typing import List, Optional
from langchain.embeddings.base import Embeddings
from config.db_config import DEFAULT_EMBEDDING_MODEL

class VectorDB:
    def __init__(self, embedding_model: Optional[Embeddings] = None):
        self.embedding_model = embedding_model
        self._init_embedding_model()
    def _init_embedding_model(self):
        """Khởi tạo embedding model"""
        if self.embedding_model == None:
            try:
                from langchain_community.embeddings import GPT4AllEmbeddings
                self.embedding_model = GPT4AllEmbeddings(model_file = DEFAULT_EMBEDDING_MODEL, device="cpu")
            except ImportError as e:
                print(str(e))
                raise ImportError("GPT4ALLEmbeddings should pip install langchain-community")

    def embed_texts(self, texts: List[str])->np.ndarray:
         """Chuyển đổi văn bản thành vector embedding"""
         vectors = self.embedding_model.embed_documents(texts)
         return np.array(vectors).astype("float32")
    def embed_query(self, query: str)->np.ndarray:
        """Chuyển đổi truy vấn thành vector embedding"""
        vector = self.embedding_model.embed_query(query)
        return np.array(vector).astype("float32").reshape(1, -1)