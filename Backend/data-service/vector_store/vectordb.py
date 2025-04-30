import os
from pathlib import Path
import json 
import logging
import pickle
import shutil
import numpy as np
import faiss
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
from langchain.schema import Document
from langchain_community.vectorstores import FAISS as LangchainFAISS
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import CharacterTextSplitter
from faiss_utils import FAISS_Utils
from faiss_io import save_faiss_index, load_faiss_index
from faiss_versioned import (
    save_index_with_version,
    load_version,
    list_index_versions,
    delete_version
)
from file_loader import DocumentProcessor
from version_manager import get_version_timestamp
from config import DATA_DIR, VECTOR_DB_DIR, DEFAULT_EMBEDDING_MODEL
@dataclass
class VectorSearchResult:
    documents: List[Document]
    distances: List[float]
    indices: List[int]

class VectorDB:
    def __init__(self, embedding_model: Optional[Embeddings] = None, data_dir = DATA_DIR, vector_db_dir = VECTOR_DB_DIR):
        self.data_dir = data_dir
        self.vector_db_dir = vector_db_dir
        self.embedding_model = embedding_model
        self._init_embedding_model()
    
    def ingest(self, source: str, faiss_name: str, chunk_size: int = 500, chunk_overlap: int = 50) -> str:
        """
        End-to-end document ingestion pipeline
        1. Load -> 2. Chunk -> 3. Embed -> 4. Index -> 5. Store
        """
        # 1. Load documents
        docs = DocumentProcessor.load(source)
        print("success load documents")
        print(docs)
        # 2. Split into chunks
        chunks = DocumentProcessor.chunk(docs, chunk_size, chunk_overlap)
        print("success chunk")
        print(chunks)
        # 3. Create embeddings and index
        vectors = self.embed_texts([chunk.page_content for chunk in chunks])
        index_dir = self.vector_db_dir/faiss_name
        if (index_dir / "index.faiss").exists():
            # Mở rộng index hiện có
            index = faiss.read_index(str(index_dir / "index.faiss"))
            new_index = FAISS_Utils.add_to_index(index, vectors)
        else:
            # Tạo index mới
            index_dir.mkdir(parents=True, exist_ok=True)
            new_index = FAISS_Utils.create_flat_index(vectors)
        print("Success create index")
        # 4. Save everything
        self._save_artifacts(new_index, faiss_name, chunks)
        return f"Ingested {len(chunks)} chunks from {source}"

    def _save_artifacts(self, index, faiss_name, chunks):
        """Save all components to disk"""
        index_dir = self.vector_db_dir/faiss_name
        faiss.write_index(index, str(index_dir / "index.faiss"))
        print(str(index_dir / "index.faiss"))
        # 2. Lưu metadata (sử dụng pickle)
        import pickle
        metadata_path = index_dir / "metadata.pkl"
        if metadata_path.exists():
            # Đọc metadata hiện có
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            existing_docs = metadata["documents"]
            # Tính offset cho ID của các chunk mới
            offset = len(existing_docs)
            # Thêm các chunk mới với ID tiếp nối
            new_docs = [{"id": i + offset, "content": chunk.page_content} for i, chunk in enumerate(chunks)]
            metadata["documents"] = existing_docs + new_docs
        else:
            # Tạo metadata mới nếu chưa tồn tại
            metadata = {
                "documents": [{"id": i, "content": chunk.page_content} for i, chunk in enumerate(chunks)],
                "total_vectors": index.ntotal
            }
        #print("metadata fjhasjgfjsgfgasgfsahfhsahfygsda", metadata)
        print(f"Length of metadata['documents']: {len(metadata['documents'])}")
        print(f"Total vectors in index: {index.ntotal}")
        with open(metadata_path, "wb") as f:
            pickle.dump(metadata, f)

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
    # ====================== Version Management ======================
    def save_index(self, 
                 index: Union[faiss.Index, LangchainFAISS], 
                 config: Optional[Dict] = None,
                 base_path: str = "faiss_index") -> str:
        """
        Lưu index với versioning
        
        Args:
            index: Index cần lưu
            config: Cấu hình metadata
            base_path: Đường dẫn cơ sở
            
        Returns:
            Version ID được tạo
        """
        config = config or {}
        return save_index_with_version(index, config, base_path)

    def load_index(self, version: str) -> Union[faiss.Index, LangchainFAISS, None]:
        """
        Tải index từ version
        
        Args:
            version: Version ID cần tải
        """
        return load_version(version, self.embedding_model)

    def list_versions(self):
        """Liệt kê tất cả các version có sẵn"""
        return list_index_versions()

    def delete_index(self, version: str):
        """Xóa một version cụ thể"""
        delete_version(version)

    # ====================== Search Functionality ======================
    def search(self, faiss_name: str, query: str,  top_k: int = 5, 
               threshold: float = 0.7, 
               include_metadata: bool = True, 
               filter_condition: Optional[dict] = None
    ) -> Dict[str, Union[List[Document], List[float], List[int]]]:
        """
        Tìm kiếm nâng cao với nhiều tùy chọn
        
        Args:
            query: Câu truy vấn đầu vào
            top_k: Số lượng kết quả trả về
            threshold: Ngưỡng điểm similarity (0-1)
            include_metadata: Có bao gồm metadata trong kết quả không
            filter_condition: Điều kiện lọc metadata (ví dụ: {"source": "doc1.pdf"})
        
        Returns:
            Dict chứa:
            - documents: List[Document] hoặc List[str]
            - scores: List[float]
            - ids: List[int]
        
        Raises:
            ValueError: Nếu index không tồn tại
            RuntimeError: Nếu có lỗi khi tìm kiếm
        """
        try:
            # 1. Kiểm tra index tồn tại
            index_dir = self.vector_db_dir / faiss_name 
            if not index_dir.exists():
                raise ValueError(f"Index not found at {index_dir}")

            # 2. Load index
            index = faiss.read_index(str(index_dir / "index.faiss"))
            # 3. Load metadata
            with open(index_dir / "metadata.pkl", "rb") as f:
                metadata = pickle.load(f)
            print(f"Index size: {index.ntotal} vectors")
            print(f"Vector dimension: {index.d}")
            print(f"Length of metadata['documents']: {len(metadata['documents'])}")
            
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
                    doc_id = indices[0][i]
                    # Kiểm tra doc_id hợp lệ
                    if doc_id < len(metadata["documents"]):
                        doc_data = metadata["documents"][doc_id]
                        print("check metadata fjsbfjbdsfbdsbfjdsbfbdsbfdsjbfv:", metadata["documents"])
                        # Tạo kết quả
                        result = {
                            "source": faiss_name,
                            "score": scores[0][i],
                            "content": doc_data["content"],
                        }
                        # Thêm metadata nếu yêu cầu
                        if include_metadata:
                            result["metadata"] = doc_data.get("metadata", {})
                        # Lọc theo filter_condition nếu có
                        # if filter_condition:
                        #     matches_filter = True
                        #     for key, value in filter_condition.items():
                        #         if result["metadata"].get(key) != value:
                        #             matches_filter = False
                        #             break
                        #     if not matches_filter:
                        #         continue
                        results.append(result)
                    else:
                        print(f"Warning: doc_id {doc_id} out of range for metadata['documents'] (length: {len(metadata['documents'])})")
            
            print("Search results:", results)
            return results
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            self._log_error(error_msg)
            raise RuntimeError(error_msg)
    def _log_error(self, message: str):
        """Ghi log lỗi đơn giản"""
        error_log = self.vector_db_dir / "errors.log"
        with open(error_log, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] {message}\n")



def main():
    manager = VectorDB()

    sources = [
        DATA_DIR/"2401.08281v3.pdf",  # File PDF
        DATA_DIR/"sample-html-files-sample2.html",  # File HTML
        "Ngày hôm nay thật vui, tôi có quen một cô gái xinh đẹp",  # Raw text
        "Tôi crush một cô gái đẹp"  # Raw text
    ]

    # Xử lý từng nguồn
    faiss_name = get_version_timestamp()
    for source in sources:
        print(f"\nProcessing: {source}")
        try:
            result = manager.ingest(
                source=source,
                faiss_name=faiss_name,
                chunk_size=500,
                chunk_overlap=50
            )
            print(f"✅ {result}")
        except Exception as e:
            print(f"❌ Error processing {source}: {str(e)}")

    # Tìm kiếm
    print("\nSearching...")
    try:
        results = manager.search(
            faiss_name=faiss_name,
            query="machine learning",
            top_k=2,
            threshold=0.6  # Ngưỡng similarity
        )
        
        for result in results:
            print(f"\n🔍 Score: {result['score']:.4f}")
            print(result['content'])
            print(result['source'])

    except Exception as e:
        print(f"Search error: {str(e)}")


if __name__ == "__main__":
    main()
