import os
import tempfile
from langchain_community.document_loaders import (
    TextLoader,
)


# Tạo tệp test trong thư mục tạm thời

# Thử ghi vào tệp
try:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as f:
        f.write("Test writing to temp directory.")
        temp_path = f.name
            
        loader = TextLoader(temp_path)
        docs = loader.load()
    print(temp_path)
    # Đọc lại tệp đã tạo để kiểm tra quyền truy cập
    with open(temp_path, "r", encoding="utf-8") as test_file:
        content = test_file.read()
        print(f"Successfully read the test file: {content}")
    
    # Xóa tệp sau khi kiểm tra
    os.remove(temp_path)
    print("Temporary test file deleted successfully.")
    
except Exception as e:
    print(f"Error accessing the temp directory: {str(e)}")
