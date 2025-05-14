import numpy as np
from typing import Any, List, Dict, Optional, Union
from langchain.embeddings.base import Embeddings

from config.config import DEFAULT_EMBEDDING_MODEL_NAME

from database.data_interface import MongoDB

class VectorDB:
    def __init__(self, embedding_model: Optional[Embeddings] = None):
        self.embedding_model = embedding_model
        self._init_embedding_model()
    def _init_embedding_model(self):
        """Khởi tạo embedding model"""
        if self.embedding_model == None:
            try:
                from langchain_community.embeddings import GPT4AllEmbeddings
                self.embedding_model = GPT4AllEmbeddings(model_name=DEFAULT_EMBEDDING_MODEL_NAME, gpt4all_kwargs={"allow_download": True})
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
    def search_vectorID(self, db_vector: MongoDB, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Tìm kiếm trong vector database dựa trên vector embedding của truy vấn.

        Args:
            db_vector: Đối tượng MongoDB để truy vấn.
            query_embedding: Vector embedding của truy vấn (danh sách float).
            top_k: Số lượng kết quả trả về.

        Returns:
            Danh sách các kết quả, mỗi kết quả là dict chứa id_mongo, embedding, score.
        """
        try:
            print(f"Mocked query vector created: {query_embedding[:5]}...")

            pipeline = [
                {
                    '$vectorSearch': {
                        'index': 'vector_index',
                        'path': 'embedding',
                        'queryVector': query_embedding,
                        'numCandidates': 150,
                        'limit': top_k,
                        'scoreDetails': True,
                    }
                },
                {
                    "$addFields": {
                        "score": {"$meta": "vectorSearchScore"}  # Thêm trường score
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "embedding": 1,
                        "id_mongo": 1,
                        "score": 1
                    }
                }
            ]

            results = list(db_vector.collection.aggregate(pipeline))
            if not results:
                print("No matches found.")
                return []

            print(f"Found {len(results)} matches:")
            for res in results:
                print(f"ID: {res['id_mongo']}, Score: {res.get('score', 'N/A')}")
            return results

        except Exception as e:
            print(f"Vector search error: {str(e)}")
            return []
    def search(self, db: MongoDB, db_vector: MongoDB, query_text: str, entities: Optional[Dict] = None, top_k:int=5, threshold: float = 0.7) -> List[Dict[str, Union[float, str]]]:
        """
        Tìm kiếm nâng cao với nhiều tùy chọn
        
        Args:
            db_vector: Đối tượng MongoDB
            query_text: Câu truy vấn đầu vào
            entities: Từ điển chứa locations, features, activities (tùy chọn)
            top_k: Số lượng kết quả trả về
            threshold: Ngưỡng điểm similarity (0-1)
        
        Returns:
            Danh sách kết quả tìm kiếm, mỗi kết quả chứa:
                - score: Điểm similarity
                - mongo_id: ID của document trong MongoDB
        """
        try:
            query_embedding = self.embed_query(query_text).reshape(-1)  # Chuyển thành 1D
            query_embedding_list = query_embedding.tolist()  # Chuyển thành danh sách cho $vectorSearch
            initial_results = self.search_vectorID(db_vector, query_embedding_list, 5 * top_k)
            mongo_ids = [result["id_mongo"] for result in initial_results]
            docs = db.fetch_from_mongodb(mongo_ids)
            doc_map = {str(doc.get("_id")): doc.get('data', {}) for doc in docs if doc.get("_id")}
            print("200 ok")
            # Re-ranking
            re_ranked_results = []
            for result in initial_results:
                mongo_id = result["id_mongo"]
                if mongo_id not in doc_map:
                    continue
                data = doc_map[mongo_id]
                content = f"{data.get('name', '')} {data.get('description', '')} {data.get('address', '')}"
                content_embedding = self.embed_texts([content])[0]
                # Điểm ngữ nghĩa
                similarity_score = np.dot(query_embedding, content_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding)
                )

                entity_boost = 0.0
                if entities:
                    address_lower = data.get("address", "").lower()
                    description_lower = data.get("description", "").lower()
                    name_lower = data.get("name", "").lower()
                    entity_boost += sum(0.5 for loc in entities.get("locations", []) if loc.lower() in address_lower)
                    entity_boost += sum(0.4 for feat in entities.get("features", []) if feat.lower() in description_lower or feat.lower() in name_lower)
                    entity_boost += sum(0.1 for act in entities.get("activities", []) if act.lower() in description_lower)

                # Tổng hợp điểm
                final_score = (similarity_score * 0.6 + entity_boost * 0.4)
                re_ranked_results.append({
                    "score": final_score,
                    "mongo_id": result["id_mongo"],
                })

            re_ranked_results.sort(key=lambda x: x["score"], reverse=True)
            return re_ranked_results[:top_k]
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            raise RuntimeError(error_msg)
   