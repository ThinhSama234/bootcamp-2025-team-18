import os
import json
from pathlib import Path
from typing import List, Union
import tempfile
from langchain.schema import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredHTMLLoader,
    WebBaseLoader
)
from langchain_text_splitters import CharacterTextSplitter

class DocumentProcessor:
    @staticmethod
    def load(source: Union[str, Path]) -> List[Document]:
        """
        Unified document loading from file path, URL or raw text
        Returns list of LangChain Documents
        
        Args:
            source: File path, URL or raw text string
            
        Returns:
            List of Document objects
        """
        # Convert Path to string if needed
        source_str = str(source) if isinstance(source, Path) else source
        
        # URL handling
        if isinstance(source_str, str) and source_str.startswith(("http://", "https://")):
            return DocumentProcessor._load_url(source_str)
        
        # File handling
        if isinstance(source_str, str) and os.path.exists(source_str):
            return DocumentProcessor._load_file(source_str)
        
        # Raw text handling
        return DocumentProcessor._load_text(source_str)

    @staticmethod
    def _load_url(url: str) -> List[Document]:
        """Load documents from URL"""
        try:
            return WebBaseLoader(url).load()
        except Exception as e:
            raise RuntimeError(f"Failed to load URL {url}: {str(e)}")

    @staticmethod
    def _load_file(file_path: str) -> List[Document]:
        """Load documents from file based on extension"""
        ext = os.path.splitext(file_path)[-1].lower()
        
        loader_map = {
            '.txt': TextLoader,
            '.pdf': PyPDFLoader,
            '.md': UnstructuredMarkdownLoader,
            '.html': UnstructuredHTMLLoader,
            '.htm': UnstructuredHTMLLoader,
            '.docx': Docx2txtLoader,
            '.csv': CSVLoader
        }
        
        if ext not in loader_map:
            raise ValueError(f"Unsupported file extension: {ext}. Supported extensions: {list(loader_map.keys())}")
        
        try:
            if ext == '.json':
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                docs = []
                if isinstance(data, list):
                    for item in data:
                        # Kiểm tra nếu không có trường 'data'
                        if 'data' not in item:
                            print(f"Warning: Skipping item without 'data' field in {file_path}")
                            continue
                        
                        data_field = item['data']
                        content = f"{data_field.get('name', '')} {data_field.get('address', '')} {data_field.get('description', '')}"
                        doc = Document(
                            page_content=content.strip(),
                            metadata={
                                "name": data_field.get("name", ""),
                                "category": data_field.get("category", ""),  # Có thể rỗng nếu không có trong JSON
                                "address": data_field.get("address", ""),
                                "description": data_field.get("description", ""),
                                "image_url": data_field.get("image_url", ""),
                                "source": file_path,
                                "type": item.get("type", ""),  # Thêm trường type
                                "created_at": item.get("created_at", None),  # Thêm trường created_at
                                "updated_at": item.get("updated_at", None)  # Thêm trường updated_at
                            }
                        )
                        if not content.strip():  # Bỏ qua nếu content rỗng
                            print(f"Warning: Skipping empty content for item {data_field.get('name', 'unknown')} in {file_path}")
                            continue
                        docs.append(doc)
                else:
                    # Kiểm tra nếu không có trường 'data'
                    if 'data' not in data:
                        raise ValueError(f"JSON file {file_path} must contain a 'data' field")
                    
                    data_field = data['data']
                    content = f"{data_field.get('name', '')} {data_field.get('address', '')} {data_field.get('description', '')}"
                    doc = Document(
                        page_content=content.strip(),
                        metadata={
                            "name": data_field.get("name", ""),
                            "category": data_field.get("category", ""),
                            "address": data_field.get("address", ""),
                            "description": data_field.get("description", ""),
                            "image_url": data_field.get("image_url", ""),
                            "source": file_path,
                            "type": data.get("type", ""),
                            "created_at": data.get("created_at", None),
                            "updated_at": data.get("updated_at", None)
                        }
                    )
                    if not content.strip():
                        raise ValueError(f"JSON file {file_path} contains empty content")
                    docs = [doc]
                return docs
            else:
                loader = loader_map[ext](file_path)
                return loader.load()
        except Exception as e:
            raise RuntimeError(f"Failed to load file {file_path}: {str(e)}")

    @staticmethod
    def _load_text(text: str) -> List[Document]:
        """Load raw text as document"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as f:
                f.write(text)
                f.flush()  # Đảm bảo dữ liệu được ghi vào file
                print(text)
                temp_path = f.name
            loader = TextLoader(temp_path, encoding='utf-8')
            print("loader", loader)
            docs = loader.load()    
            print(f"Documents loaded: {docs[:1]}")
            os.remove(temp_path)
            print("Temporary test file deleted successfully.")
            return docs     
        except Exception as e:
            if 'temp_path' in locals():
                try:
                    os.remove(temp_path)
                except:
                    pass
            raise RuntimeError(f"Failed to load text: {str(e)}")

    @staticmethod
    def chunk(
        documents: List[Document], 
        chunk_size: int = 500, 
        chunk_overlap: int = 50
    ) -> List[Document]:
        """Split documents into chunks with metadata preservation"""
        text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True
        )
        
        try:
            chunks = []
            for doc in documents:
                split_docs = text_splitter.split_documents([doc])
                for split_doc in split_docs:
                    split_doc.metadata = doc.metadata
                    chunks.append(split_doc)
            return chunks
        except Exception as e:
            raise RuntimeError(f"Failed to chunk documents: {str(e)}")