import os
import shutil
from typing import Dict, Optional, Union
from datetime import datetime
import faiss
from langchain_community.vectorstores import FAISS as LangchainFAISS
from langchain.embeddings.base import Embeddings

from .faiss_io import save_faiss_index, load_faiss_index
from .version_manager import get_version_timestamp, load_version_log, save_version_log

def save_index_with_version(
    index: Union[LangchainFAISS, faiss.Index], 
    config: dict, 
    base_path: str = "faiss_index"
) -> str:
    """Lưu index kèm thông tin version"""
    version = get_version_timestamp()
    full_path = f"{base_path}_{version}"

    if isinstance(index, LangchainFAISS):
        index.save_local(full_path)
        print(f"[langchain-FAISS] Saved successfully to {full_path}")
    elif isinstance(index, faiss.Index):
        os.makedirs(full_path, exist_ok=True)
        index_file = os.path.join(full_path, "index.faiss")
        save_faiss_index(index, index_file)
    else:
        raise TypeError("Unsupported index type")

    log = load_version_log()
    log[version] = {
        "path": full_path,
        "created_at": datetime.now().isoformat(),
        "config": config,
        "index_type": type(index).__name__
    }
    save_version_log(log)
    return version

def list_index_versions():
    """Liệt kê tất cả các version có sẵn"""
    log = load_version_log()
    if not log:
        print("[i] Empty database")
        return
    for version, info in sorted(log.items(), reverse=True):
        print(f"{version}: {info['path']} (type: {info.get('index_type', 'unknown')})")

def load_version(
    version: str, 
    embedding_model: Optional[Embeddings] = None
) -> Union[LangchainFAISS, faiss.Index, None]:
    """Tải index từ version cụ thể"""
    log = load_version_log()
    if version not in log:
        print(f"[x] Version {version} not found")
        return None
    
    info = log[version]
    path = info['path']
    index_type = info.get('index_type')

    if index_type == 'FAISS':  # langchain FAISS
        return LangchainFAISS.load_local(
            path, 
            embedding_model, 
            allow_dangerous_deserialization=True
        )
    elif index_type.startswith(("Index", "faiss.")):
        index_file = os.path.join(path, "index.faiss")
        return load_faiss_index(index_file)
    else:
        print(f"[x] Unknown index type '{index_type}'")
        return None

def delete_version(version: str):
    """Xóa version cụ thể"""
    log = load_version_log()
    if version not in log:
        print(f"[x] Cannot delete: version {version} not found")
        return
    
    path = log[version]['path']
    try:
        shutil.rmtree(path)
        print(f"[✓] Deleted folder: {path}")
    except Exception as e:
        print(f"[x] Error deleting folder: {e}")
    
    del log[version]
    save_version_log(log)
    print(f"[✓] Removed version {version} from log")