import os
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
                temp_path = f.name
            
            loader = TextLoader(temp_path)
            docs = loader.load()
            
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
                
            return docs
        except Exception as e:
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
                chunks.extend(text_splitter.split_documents([doc]))
            return chunks
        except Exception as e:
            raise RuntimeError(f"Failed to chunk documents: {str(e)}")