import os
import faiss

def save_faiss_index(index: faiss.Index, file_path: str = "vector.index"):
    """Lưu index FAISS vào file"""
    faiss.write_index(index, file_path)
    print(f"[faiss] Saved native index to '{file_path}'")

def load_faiss_index(file_path: str = "vector.index") -> faiss.Index:
    """Đọc index FAISS từ file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Index file '{file_path}' not found.")
    index = faiss.read_index(file_path)
    print(f"[faiss] Loaded native index from '{file_path}'")
    return index