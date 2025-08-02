import tiktoken
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from ..core.settings import settings


class DocumentLoaderService:
    """Service for loading and processing federal ethics documents"""
    
    def __init__(self):
        self.text_splitter = self._create_text_splitter()
    
    def _create_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create text splitter with tiktoken length function"""
        def tiktoken_length_function(text: str) -> int:
            tokens = tiktoken.encoding_for_model("gpt-4o").encode(text)
            return len(tokens)
        
        return RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=tiktoken_length_function
        )
    
    def load_ethics_documents(self) -> List[Document]:
        """Load federal ethics law documents from data directory"""
        try:
            directory_loader = DirectoryLoader(
                settings.data_directory,
                glob="**/*.pdf",
                loader_cls=PyMuPDFLoader
            )
            
            documents = directory_loader.load()
            print(f"📚 Loaded {len(documents)} pages from federal ethics laws")
            
            return documents
            
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            return []
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks for vector storage"""
        try:
            chunks = self.text_splitter.split_documents(documents)
            
            avg_chunk_size = sum(len(chunk.page_content) for chunk in chunks) // len(chunks)
            print(f"🔄 Split {len(documents)} pages into {len(chunks)} chunks")
            print(f"📊 Average chunk size: {avg_chunk_size} characters")
            
            return chunks
            
        except Exception as e:
            print(f"❌ Error splitting documents: {e}")
            return documents
    
    def load_and_split_documents(self) -> List[Document]:
        """Load and split ethics documents in one operation"""
        documents = self.load_ethics_documents()
        if not documents:
            return []
            
        return self.split_documents(documents)


