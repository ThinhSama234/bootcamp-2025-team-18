📚 Vector DB Manager
Hệ thống quản lý và tìm kiếm dữ liệu văn bản sử dụng FAISS cho việc indexing và tìm kiếm hiệu quả, hỗ trợ nhiều loại nguồn dữ liệu (PDF, HTML, raw text...). Dữ liệu sau khi xử lý sẽ được lưu trữ theo từng phiên bản (versioned indexing) giúp quản lý lịch sử dễ dàng và linh hoạt.

🗂️ Cấu trúc thư mục
text
Sao chép
Chỉnh sửa
├── vector_db/            # Lưu trữ các FAISS index đã tạo, mỗi thư mục là một phiên bản theo timestamp
├── models/               # Chứa model embedding
├── data/                 # Dữ liệu thô: PDF, HTML, text...
├── config.py             # Cấu hình hệ thống (đường dẫn, tham số...)
├── faiss_utils.py        # Các chiến lược tạo FAISS index
├── load_utils.py         # Cơ chế đọc dữ liệu từ nhiều định dạng
├── faiss_versioned.py    # Quản lý thêm, xóa, hiển thị các version FAISS
├── vector_db_manager.py  # Quản lý ingest và search vào Vector DB
├── demo.py               # Demo đơn giản cách sử dụng
├── demo_wrapper.py       # Demo đầy đủ, tự động hóa quy trình ingest & search
🚀 Cách sử dụng nhanh
File demo mẫu: demo_wrapper.py

1. Ingest dữ liệu vào Vector DB
python
Sao chép
Chỉnh sửa
from vector_db_manager import VectorDBManager
from config import DATA_DIR
from version_manager import get_version_timestamp

# Khởi tạo manager
manager = VectorDBManager()

# Danh sách nguồn dữ liệu
sources = [
    DATA_DIR/"2401.08281v3.pdf",        # File PDF
    DATA_DIR/"sample-html-files-sample2.html",  # HTML
    "Ngày hôm nay thật vui, tôi có quen một cô gái xinh đẹp",  # Văn bản thô
    "Tôi crush một cô gái đẹp"         # Văn bản thô
]

# Tạo tên phiên bản FAISS mới
faiss_name = get_version_timestamp()

# Ingest từng nguồn
for source in sources:
    result = manager.ingest(
        source=source,
        faiss_name=faiss_name,
        chunk_size=500,
        chunk_overlap=50
    )
    print(result)
2. Tìm kiếm
python
Sao chép
Chỉnh sửa
results = manager.search(
    faiss_name=faiss_name,
    query="machine learning",
    top_k=2,
    threshold=0.6
)

for result in results:
    print(f"Score: {result['score']:.4f}")
    print(result['content'])
    print(result['source'])
⚙️ Chi tiết các bước trong ingest()
Hàm ingest() thực hiện toàn bộ pipeline:

Load dữ liệu: Đọc từ file PDF, HTML hoặc chuỗi văn bản.

Chunk: Chia văn bản thành các đoạn nhỏ (chunk) theo chunk_size và chunk_overlap.

Embed: Ánh xạ mỗi chunk thành vector embedding.

Index: Chọn chiến lược indexing (Flat, IVF, HNSW...) và tạo FAISS index.

Store: Lưu kết quả vào thư mục riêng biệt (theo timestamp).

🧠 Chiến lược indexing (FAISS)
Hệ thống hỗ trợ nhiều loại FAISS index để cân bằng giữa tốc độ và độ chính xác:


Tên	Mô tả	Ưu điểm	Nhược điểm
Flat (IndexFlatL2/IP)	Tìm kiếm chính xác tuyệt đối bằng khoảng cách Euclidean hoặc Inner Product	Đơn giản, chính xác 100%	Chậm khi dữ liệu lớn
IVF (IndexIVFFlat)	Chia dữ liệu thành nlist cụm, chỉ tìm trong một số cụm gần nhất (nprobe)	Tăng tốc đáng kể, cân bằng hiệu suất và tốc độ	Cần train trước, kết quả gần đúng
IVF + PQ (IndexIVFPQ)	Kết hợp IVF với kỹ thuật nén (Product Quantization) để tiết kiệm bộ nhớ	Phù hợp với dataset rất lớn	Giảm độ chính xác
HNSW (IndexHNSWFlat)	Cấu trúc đồ thị nhỏ thế giới (Hierarchical Navigable Small World), tìm kiếm gần đúng nhưng rất nhanh	Rất nhanh, phù hợp real-time search	Tối ưu trên nhiều config khác nhau
📦 Ghi chú thêm
Dữ liệu đã index sẽ được lưu tại thư mục vector_db/ với tên tương ứng version.faiss/index.faiss.

Có thể dùng các hàm như list_versions(), load_index(version) để thao tác với các phiên bản khác nhau.

Các chiến lược indexing có thể mở rộng thêm hoặc tùy chỉnh thông qua file faiss_utils.py.

🛠️ Yêu cầu
bash
Sao chép
Chỉnh sửa
pip install -r requirements.txt
Bao gồm:

faiss-cpu

numpy

pdfplumber, beautifulsoup4, v.v. (cho việc xử lý file)
