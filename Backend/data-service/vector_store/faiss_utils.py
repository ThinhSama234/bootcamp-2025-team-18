from typing import Tuple
import numpy as np
import faiss
import json
class FAISS_Utils: 
    # ================= Metric ========
    METRIC_L2 = faiss.METRIC_L2
    METRIC_INNER_PRODUCT = faiss.METRIC_INNER_PRODUCT
    # ============= PCA ===========
    @staticmethod
    def add_to_index(index, new_vectors):
        """Thêm vectors vào index hiện có"""
        index.add(new_vectors)
        return index
    @staticmethod
    def add_to_index_with_ids(index, new_vectors, ids):
        """Thêm vectors vào index có ID"""
        assert isinstance(index, faiss.IndexIDMap), "Index must be IndexIDMap to add with IDs"
        index.add_with_ids(new_vectors, ids)
        return index
    @staticmethod
    def pca_reduce(data, input_dim, output_dim):
        pca = faiss.PCAMatrix(input_dim, output_dim)
        pca.train(data)
        assert pca.is_trained, "PCA is failed"
        return pca.apply(data)
    # ============= Index plat (exact search) ======= 
    @staticmethod
    def create_flat_index(data, ids=None, metric_type = faiss.METRIC_L2):
        """Tạo index tìm kiếm chính xác (exact search)"""
        d = data.shape[1]
        print("metric_type:", metric_type)
        if metric_type == faiss.METRIC_L2:
            index = faiss.IndexFlatL2(d)
        else:
            index = faiss.IndexFlatIP(d)
        if ids is not None:
            return FAISS_Utils.wrap_with_ids(index, data, ids)
        index.add(data)
        return index
    # ======== kmeans => index flat =========
    @staticmethod
    def create_ivf_index(data, ids = None, nlist = 100, nprobe = 10, metric_type = METRIC_L2):
        """Tạo index IVF (Inverted File) để tìm kiếm gần đúng"""
        d = data.shape[1]
        quantizer = faiss.IndexFlatL2(d) if metric_type == FAISS_Utils.METRIC_L2 else faiss.IndexFlatIP(d)
        index = faiss.IndexIVFFlat(quantizer, d, nlist, metric_type)
        index.train(data)
        assert index.is_trained, "IVF training failed"
        if ids is not None:
            return FAISS_Utils.wrap_with_ids(index, data, ids, nprobe)
        index.add(data)
        index.nprobe = nprobe
        return index
    # -------------------- INDEX IVF PQ --------------------
    @staticmethod
    def create_ivfpq_index(data, ids = None, nlist=100, m=8, nbits=8, metric_type=METRIC_L2):
        """Tạo index IVF với Product Quantization để giảm dung lượng"""
        d = data.shape[1]
        quantizer = faiss.IndexFlatL2(d) if metric_type == FAISS_Utils.METRIC_L2 else faiss.IndexFlatIP(d)
        index = faiss.IndexIVFPQ(quantizer, d, nlist, m, nbits, metric_type)
        index.train(data)
        assert index.is_trained, "IVF PQ training failed"
        if ids is not None:
            return FAISS_Utils.wrap_with_ids(index, data, ids)
        index.add(data)
        return index

    # -------------------- INDEX HNSW --------------------
    @staticmethod
    def create_hnsw_index(data, ids = None, hnsw_m=32, metric_type=METRIC_L2):
        """Tạo index HNSW (Hierarchical Navigable Small World)"""
        d = data.shape[1]
        index = faiss.IndexHNSWFlat(d, hnsw_m, metric_type)
        if ids is not None:
            return FAISS_Utils.wrap_with_ids(index, data, ids)
        index.add(data)
        return index

    # ========= search function ==================
    def search_index(index, queries, top_k = 5, nprobe= None)->Tuple[np.ndarray, np.ndarray]:
        if hasattr(index, 'nprobe') and nprobe is not None:
            index.nprobe = nprobe
        D, I = index.search(queries, top_k)
        print("In ra distances, va index cua ket qua")
        return D, I
    # ============ Wrapper with ID =============
    @staticmethod
    def wrap_with_ids(index, vectors: np.ndarray, ids: np.ndarray, nprobe=None):
        """Gói Index bất kỳ thành IndexIDMap để gán ID"""
        id_index = faiss.IndexIDMap(index)
        id_index.add_with_ids(vectors, ids)
        if nprobe and hasattr(id_index, 'nprobe'):
            id_index.nprobe = nprobe
        return id_index
    # ============ Save / Load ID map ============
    @staticmethod
    def save_id_map(id_map: dict, path):
        with open(path, 'w') as f:
            json.dump(id_map, f)

    @staticmethod
    def load_id_map(path) -> dict:
        with open(path) as f:
            return json.load(f)