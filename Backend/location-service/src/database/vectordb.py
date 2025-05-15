import numpy as np
from typing import Any, List, Dict, Optional, Union
from langchain.embeddings.base import Embeddings

from config.config import DEFAULT_EMBEDDING_MODEL_NAME

from database.data_interface import MongoDB


from geopy.distance import geodesic

import traceback
MAX_DISTANCE_DEFAULT = 5000
CANDIDATE_MULTIPLIER = 10
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
    def search_vectorID(self, db: MongoDB, db_vector: MongoDB, coordinates: List[float], query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
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
                        'index': 'default',
                        'path': 'embedding',
                        'queryVector': query_embedding,
                        'numCandidates': 150,
                        'limit': top_k,
                        'scoreDetails': True,
                    }
                },
                {
                    "$addFields": {
                        "score": {"$meta": "vectorSearchScore"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id_mongo": 1,
                        "score": 1,
                    }
                }
            ]

            results = list(db_vector.collection.aggregate(pipeline))
            mongo_ids = [result["id_mongo"] for result in results]
            docs = db.fetch_from_mongodb(mongo_ids)
            doc_map = {str(doc.get("_id")): doc for doc in docs if doc.get("_id")}
    
            if coordinates is not None:
                if not results:
                    print("No matches found.")
                    return []

                for res in results:
                    mongo_id = res["id_mongo"]
                    if mongo_id not in doc_map:
                        continue
                    value = doc_map[mongo_id]
                    location = value.get("location", {})
                    if location:
                        loc = location.get("coordinates")
                        if loc:
                            dist = geodesic((coordinates[0], coordinates[1]), (loc[1], loc[0])).meters
                            res["calcDistance"] = dist
                        else:
                            res["calcDistance"] = None
                    else:
                        res["calcDistance"] = None

            print(f"Found {len(results)} matches:")
            seen = set()
            unique_results = []
            for res in results:
                _id = res["id_mongo"]
                if _id not in seen:
                    unique_results.append(res)
                    seen.add(_id)
                # if res.get("calcDistance") is not None:
                #     print(f"ID: {res.get('id_mongo')}, Score: {res.get('score')}, dist {res.get('calcDistance')} m")
                # else:
                #     print(f"ID: {res.get('id_mongo')}, Score: {res.get('score')}, m")
            #print(f"lọc trùng ra {len(unique_results)} matches:")
            return doc_map, unique_results
        except Exception as e:
            print(f"Vector + Geo search error: {e}")
            #traceback.print_exc()
            return []


    def search(self, db: MongoDB, db_vector: MongoDB, query_text: str, entities: Optional[Dict] = None, top_k:int=5, threshold: float = 0.7, coordinates: Optional[List[float]] = None, max_distance: float = MAX_DISTANCE_DEFAULT,) -> List[Dict[str, Union[float, str]]]:
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
            # Step 1: Lấy embedding từ query
            query_embedding = self.embed_query(query_text).reshape(-1)
            query_embedding_list = query_embedding.tolist()

            # Step 2: Tìm top vector candidates (lấy nhiều hơn để rerank)
            doc_map, initial_results = self.search_vectorID(db, db_vector, coordinates, query_embedding_list, 5 * top_k)

            # Step 4: Tìm min-max distance để chuẩn hóa
            distances = [res.get("calcDistance") for res in initial_results if res.get("calcDistance") is not None]
            min_dist = min(distances) if distances else 0
            max_dist = max(distances) if distances else 1  # tránh chia 0

            re_ranked_results = []
            for result in initial_results:
                mongo_id = result["id_mongo"]
                if mongo_id not in doc_map:
                    continue
                data = doc_map[mongo_id].get('data', {})
                content = f"{data.get('name', '')} {data.get('description', '')} {data.get('address', '')}"
                content_embedding = self.embed_texts([content])[0]

                # Similarity
                similarity_score = np.dot(query_embedding, content_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding)
                )

                # Distance score (chuẩn hóa về [0,1] và đảo ngược lại: gần hơn thì điểm cao hơn)
                raw_distance = result.get("calcDistance")
                if raw_distance is not None and max_dist != min_dist:
                    distance_score = 1 - (raw_distance - min_dist) / (max_dist - min_dist)
                else:
                    distance_score = 0  # nếu không có location thì không cộng
                # Entity boost
                entity_boost = 0.0
                if entities:
                    address_lower = data.get("address", "").lower()
                    description_lower = data.get("description", "").lower()
                    name_lower = data.get("name", "").lower()
                    entity_boost += sum(0.5 for loc in entities.get("locations", []) if loc.lower() in address_lower)
                    entity_boost += sum(0.4 for feat in entities.get("features", []) if feat.lower() in description_lower or feat.lower() in name_lower)
                    entity_boost += sum(0.1 for act in entities.get("activities", []) if act.lower() in description_lower)
                #print(f"Tong hop diem:, {mongo_id}, {similarity_score}, {entity_boost}, {distance_score}")
                # Tổng hợp điểm rerank
                if distance_score:
                    final_score = similarity_score * 0.5 + entity_boost * 0.3 + distance_score * 0.2
                else:
                    final_score = similarity_score * 0.6 + entity_boost * 0.4 
                re_ranked_results.append({
                    "score": final_score,
                    "mongo_id": mongo_id,
                })

            # Step 5: Sort theo điểm
            re_ranked_results.sort(key=lambda x: x["score"], reverse=True)
            return re_ranked_results[:top_k]

        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            raise RuntimeError(error_msg)
   