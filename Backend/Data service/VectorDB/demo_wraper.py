from vector_db_manager import VectorDBManager
from config import DATA_DIR
from version_manager import get_version_timestamp

# Khởi tạo manager
manager = VectorDBManager()

# Danh sách nguồn dữ liệu
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
        print(f"\n🔍 Score: {result["score"]:.4f}")
        print(result["content"])
        print(result["source"])

except Exception as e:
    print(f"Search error: {str(e)}")

# Quản lý version
# print("\nVersion Management:")
# versions = manager.list_versions()  # Trả về dict {version: info}
# if versions:
#     latest_version = next(iter(versions.items()))[0]  # Lấy version mới nhất
#     print(f"Latest version: {latest_version}")
    
#     # Tải lại index
#     try:
#         print("\nReloading index...")
#         reloaded_index = manager.load_index(latest_version)
#         print(f"✅ Successfully reloaded version {latest_version}")
#     except Exception as e:
#         print(f"❌ Failed to reload: {str(e)}")
# else:
#     print("No versions available")