import json 
import numpy as np
import faiss
from typing import List, Dict, Optional, Union
from langchain.schema import Document
from langchain_community.vectorstores import FAISS as LangchainFAISS
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import CharacterTextSplitter
from .faiss_utils import FAISS_Utils
from .faiss_io import save_faiss_index, load_faiss_index
from .file_loader import DocumentProcessor
from .version_manager import get_version_timestamp
from .config import DATA_DIR, VECTOR_DB_DIR, DEFAULT_EMBEDDING_MODEL

class VectorDB:
    def __init__(self, embedding_model: Optional[Embeddings] = None, data_dir = DATA_DIR, vector_db_dir = VECTOR_DB_DIR):
        self.data_dir = data_dir
        self.vector_db_dir = vector_db_dir
        self.embedding_model = embedding_model
        self._init_embedding_model()
    
    def ingest(self, source: str, faiss_name: str, chunk_size: int = 500, chunk_overlap: int = 50, _id: str = None) -> str:
        """
        End-to-end document ingestion pipeline
        1. Load -> 2. Chunk -> 3. Embed -> 4. Index -> 5. Store
        """
        # 1. Load documents
        docs = DocumentProcessor.load(source)
        print("success load documents")
        # 2. Split into chunks
        chunks = DocumentProcessor.chunk(docs, chunk_size, chunk_overlap)
        print("success chunk")
        # 3. Create embeddings and index
        vectors = self.embed_texts([chunk.page_content for chunk in chunks])
        # 4. Chuẩn bị ánh xạ FAISS ID ↔ Mongo ID
        mongo_ids = [str(_id)] * len(chunks)
        if len(chunks) > 1:
            print(f"Warning: {len(chunks)} chunks created from {_id}.")
        index_dir = self.vector_db_dir/faiss_name
        index_path = index_dir / "index.faiss"
        id_map_path = index_dir / "map_id.json"
        if index_path.exists():
            # Mở rộng index hiện có
            index = faiss.read_index(str(index_path))
            offset = index.ntotal
            faiss_ids = np.arange(offset, offset+len(mongo_ids)).astype("int64")
            index = faiss.IndexIDMap(index) if not isinstance(index, faiss.IndexIDMap) else index
            FAISS_Utils.add_to_index_with_ids(index, vectors, faiss_ids)
            new_index = index
        else:
            # Tạo index mới
            index_dir.mkdir(parents=True, exist_ok=True)
            faiss_ids = np.arange(len(mongo_ids)).astype("int64")
            new_index = FAISS_Utils.create_flat_index(vectors, faiss_ids)
        if id_map_path.exists():
            with open(id_map_path) as f:
                old_id_map = json.load(f)
        else:
            old_id_map = {}

        new_id_map = {int(fid): mid for fid, mid in zip(faiss_ids, mongo_ids)}
        merged_id_map = {**old_id_map, **new_id_map}
        # save merge
        FAISS_Utils.save_id_map(merged_id_map, id_map_path)
        print("Success create index")
        # 5. Save everything
        self._save_artifacts(new_index, faiss_name, chunks)
        return f"{len(chunks)} chunks from {_id}"

    def _save_artifacts(self, index, faiss_name, chunks):
        """Save all components to disk"""
        index_dir = self.vector_db_dir/faiss_name
        faiss.write_index(index, str(index_dir / "index.faiss"))
        print(str(index_dir / "index.faiss"))
        print(f"Total vectors in index: {index.ntotal}")

    def _init_embedding_model(self):
        """Khởi tạo embedding model"""
        if self.embedding_model == None:
            try:
                from langchain_community.embeddings import GPT4AllEmbeddings
                self.embedding_model = GPT4AllEmbeddings(model_file = DEFAULT_EMBEDDING_MODEL)
            except ImportError:
                raise ImportError("GPT4ALLEmbeddings should pip install langchain-community")

    def embed_texts(self, texts: List[str])->np.ndarray:
         """Chuyển đổi văn bản thành vector embedding"""
         vectors = self.embedding_model.embed_documents(texts)
         return np.array(vectors).astype("float32")
    def embed_query(self, query: str)->np.ndarray:
        """Chuyển đổi truy vấn thành vector embedding"""
        vector = self.embedding_model.embed_query(query)
        return np.array(vector).astype("float32").reshape(1, -1)
    def create_index(self, texts: List[str], index_type: str = "flat", **index_params)->Union[faiss.Index, LangchainFAISS]:
        """
        tạo index từ file faiss_utils
        args:
        texts
        index_type: Loại index ('flat', 'ivf', 'ivfpq', 'hnsw', 'langchain')
        **index_params: tham số tùy chỉnh cho từng loại
        """
        vectors = self.embed_texts(texts)
        if index_type == "langchain":
            documents = [Document(page_content=text) for text in texts]
            return LangchainFAISS.from_documents(documents, self.embedding_model)
        
        if index_type == "flat":
            return FAISS_Utils.create_flat_index(vectors, **index_params)
        elif index_type == "ivf":
            return FAISS_Utils.create_ivf_index(vectors, **index_params)
        elif index_type == "ivfpq":
            return FAISS_Utils.create_ivfpq_index(vectors, **index_params)
        elif index_type == "hnsw":
            return FAISS_Utils.create_hnsw_index(vectors, **index_params)
        else:
            raise ValueError(f"Unknown index type: {index_type}")
    def search(self, faiss_name: str, query: str,  top_k: int = 5, 
               threshold: float = 0.7, 
    ) -> Dict[str, Union[List[Document], List[float], List[int]]]:
        """
        Tìm kiếm nâng cao với nhiều tùy chọn
        
        Args:
            query: Câu truy vấn đầu vào
            top_k: Số lượng kết quả trả về
            threshold: Ngưỡng điểm similarity (0-1)
        
        Returns:
            results: Danh sách kết quả tìm kiếm, mỗi kết quả là một dict chứa:
                - source: Tên nguồn (faiss_name)
                - score: Điểm similarity
                - mongo_id: ID của document trong MongoDB
        """
        try:
            # 1. Kiểm tra index tồn tại
            index_dir = self.vector_db_dir / faiss_name 
            if not index_dir.exists():
                raise ValueError(f"Index not found at {index_dir}")

            # 2. Load index
            index = faiss.read_index(str(index_dir / "index.faiss"))
            # 3. Load metadata
            with open(index_dir/ "map_id.json", "r", encoding="utf-8") as f:
                id_map = json.load(f)
                mongo_id = {int(k): v for k, v in id_map.items()} # 👈 ép key về int
            print("loaded successfully map id faiss <-> mongo")
            print(f"Index size: {index.ntotal} vectors")
            print(f"Vector dimension: {index.d}")

            # 4. Chuyển query thành vector
            query_vector = self.embed_query(query)
            print("Query vector norm:", np.linalg.norm(query_vector))
            
            # 5. Thực hiện tìm kiếm
            scores, indices = index.search(query_vector, top_k)
            # 6. Xử lý kết quả
            results = []
            for i in range(len(indices[0])):
                print(f"Score: {scores[0][i]}, Index: {indices[0][i]}")
                # So sánh khoảng cách (nhỏ hơn threshold thì giữ lại)
                if scores[0][i] <= threshold:
                    doc_id = int(indices[0][i])
                    result = {
                        "source": faiss_name,
                        "score": scores[0][i],
                        "mongo_id": mongo_id[doc_id],
                    }
                    results.append(result)
            return results
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            raise RuntimeError(error_msg)

