import json 
import numpy as np
from typing import List, Dict, Optional, Union
from langchain.embeddings.base import Embeddings
from .config import VECTOR_DB_DIR, DEFAULT_EMBEDDING_MODEL
from data_interface import MongoDB
from extract_metadata import fetch_from_mongodb
class VectorDB:
    def __init__(self, embedding_model: Optional[Embeddings] = None, vector_db_dir = VECTOR_DB_DIR):
        self.vector_db_dir = vector_db_dir
        self.embedding_model = embedding_model
        self._init_embedding_model()
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
    def search_vectorID(self, db_vector: MongoDB, query_text: str = "", top_k: int = 5):
        query_vector = self.embed_query(query_text).tolist()
        print(f"Mocked query vector created: {query_vector[:5]}...")
        pipeline = [
        {
            '$vectorSearch': {
            'index': 'vector_index', 
            'path': 'embedding', 
            'queryVector': query_vector, 
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
        }]

        results = list(db_vector.collection.aggregate(pipeline))
        if not results:
            print("No matches found.")
            return []
        
        print(f"Found {len(results)} matches:")
        for res in results:
            print(f"ID: {res['id_mongo']}, Score: {res.get('score', 'N/A')}")
        return results
    def search(self, db_vector: MongoDB, query_text: str, entities: Optional[Dict] = None, top_k:int=5, threshold: float = 0.7) -> Dict[str, Union[List[Document], List[float], List[int]]]:
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
            initial_results = self.search_vectorID(db_vector, query_text, top_k)
            mongo_ids = [result["id_mongo"] for result in initial_results]
            docs = fetch_from_mongodb(mongo_ids)
            doc_map = {str(doc.get("_id")): doc.get('data', {}) for doc in docs if doc.get("_id")}

            # Re-ranking
            query_embedding = self.embed_query(query_text)
            re_ranked_results = []
            for result in initial_results:
                mongo_id = result["id_mongo"]
                if mongo_id not in doc_map:
                    continue
                data = doc_map[mongo_id]
                content = f"{data.get('name', '')} {data.get('description', '')} {data.get('address', '')}"
                #print(f"description: {data.get('description', '')}")
                content_embedding = self.embed_texts([content])[0]
                # Điểm ngữ nghĩa
                similarity_score = np.dot(query_embedding, content_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding)
                )
                #print(f"similarity_score: {similarity_score}")

                entity_boost = 0.0
                if entities:
                    # Khớp với locations
                    locations = entities.get("locations", [])
                    for location in locations:
                        if location.lower() in data.get("address", "").lower():
                            entity_boost += 0.5
                    # Khớp với features
                    features = entities.get("features", [])
                    for feature in features:
                        if feature.lower() in data.get("description", "").lower() or feature.lower() in data.get("name", "").lower():
                            entity_boost += 0.4
                    # Khớp với activities
                    activities = entities.get("activities", [])
                    for activity in activities:
                        if activity.lower() in data.get("description", "").lower():
                            entity_boost += 0.1

                # Tổng hợp điểm
                final_score = (similarity_score * 0.6 + entity_boost * 0.4)
                re_ranked_results.append({
                    "source": result["source"],
                    "score": final_score,
                    "mongo_id": result["id_mongo"],
                })

            re_ranked_results.sort(key=lambda x: x["score"], reverse=True)
            return re_ranked_results[:top_k]
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            raise RuntimeError(error_msg)
    # def search(self, faiss_name: str, query: str, entities: Optional[Dict] = None, top_k: int = 5, 
    #            threshold: float = 0.7, 
    # ) -> Dict[str, Union[List[Document], List[float], List[int]]]:
    #     """
    #     Tìm kiếm nâng cao với nhiều tùy chọn
        
    #     Args:
    #         query: Câu truy vấn đầu vào
    #         top_k: Số lượng kết quả trả về
    #         threshold: Ngưỡng điểm similarity (0-1)
        
    #     Returns:
    #         results: Danh sách kết quả tìm kiếm, mỗi kết quả là một dict chứa:
    #             - source: Tên nguồn (faiss_name)
    #             - score: Điểm similarity
    #             - mongo_id: ID của document trong MongoDB
    #     """
    #     try:
    #         # 1. Kiểm tra index tồn tại
    #         index_dir = self.vector_db_dir / faiss_name 
    #         if not index_dir.exists():
    #             raise ValueError(f"Index not found at {index_dir}")

    #         # 2. Load index
    #         index = faiss.read_index(str(index_dir / "index.faiss"))
    #         # 3. Load metadata
    #         with open(index_dir/ "map_id.json", "r", encoding="utf-8") as f:
    #             id_map = json.load(f)
    #             mongo_id = {int(k): v for k, v in id_map.items()} # 👈 ép key về int
    #         print("loaded successfully map id faiss <-> mongo")
    #         print(f"Index size: {index.ntotal} vectors")
    #         print(f"Vector dimension: {index.d}")

    #         # 4. Chuyển query thành vector
    #         query_vector = self.embed_query(query)
    #         print("Query vector norm:", np.linalg.norm(query_vector))
            
    #         # 5. Thực hiện tìm kiếm
    #         scores, indices = index.search(query_vector, top_k)
    #         # 6. Xử lý kết quả
    #         initial_results = []
    #         for i in range(len(indices[0])):
    #             #print(f"Score: {scores[0][i]}, Index: {indices[0][i]}")
    #             if scores[0][i] >= threshold:
    #                 doc_id = int(indices[0][i])
    #                 result = {
    #                     "source": faiss_name,
    #                     "score": scores[0][i],
    #                     "mongo_id": mongo_id[doc_id],
    #                 }
    #                 print(f"Score: {scores[0][i]}, id: {mongo_id[doc_id]}")
    #                 initial_results.append(result)

    #         #return initial_results
    #         mongo_ids = [result["mongo_id"] for result in initial_results]
    #         docs = fetch_from_mongodb(mongo_ids, URL="vietnamtourism_URL", collection="vietnamtourism_db", document="vietnamtourism_db")
    #         doc_map = {str(doc.get("_id")): doc.get('data', {}) for doc in docs if doc.get("_id")}

    #         # Re-ranking
    #         query_embedding = self.embed_query(query)
    #         re_ranked_results = []
    #         for result in initial_results:
    #             mongo_id = result["mongo_id"]
    #             if mongo_id not in doc_map:
    #                 continue
    #             data = doc_map[mongo_id]
    #             content = f"{data.get('name', '')} {data.get('description', '')} {data.get('address', '')}"
    #             #print(f"description: {data.get('description', '')}")
    #             content_embedding = self.embed_texts([content])[0]
    #             # Điểm ngữ nghĩa
    #             similarity_score = np.dot(query_embedding, content_embedding) / (
    #                 np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding)
    #             )
    #             #print(f"similarity_score: {similarity_score}")

    #             entity_boost = 0.0
    #             if entities:
    #                 # Khớp với locations
    #                 locations = entities.get("locations", [])
    #                 for location in locations:
    #                     if location.lower() in data.get("address", "").lower():
    #                         entity_boost += 0.5
    #                 # Khớp với features
    #                 features = entities.get("features", [])
    #                 for feature in features:
    #                     if feature.lower() in data.get("description", "").lower() or feature.lower() in data.get("name", "").lower():
    #                         entity_boost += 0.4
    #                 # Khớp với activities
    #                 activities = entities.get("activities", [])
    #                 for activity in activities:
    #                     if activity.lower() in data.get("description", "").lower():
    #                         entity_boost += 0.1

    #             # Tổng hợp điểm
    #             final_score = (similarity_score * 0.6 + entity_boost * 0.4)
    #             re_ranked_results.append({
    #                 "source": result["source"],
    #                 "score": final_score,
    #                 "mongo_id": result["mongo_id"],
    #             })

    #         re_ranked_results.sort(key=lambda x: x["score"], reverse=True)
    #         return re_ranked_results[:top_k]
    #     except Exception as e:
    #         error_msg = f"Search failed: {str(e)}"
    #         raise RuntimeError(error_msg)

# results = manager.search(
#                 faiss_name=self.faiss_name,
#                 query=state['summary'],
#                 entities=state["entities"],
#                 top_k=k,
#                 threshold=0.2
#             )
