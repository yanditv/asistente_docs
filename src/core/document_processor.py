"""
Document processing and text splitting functionality
"""
import hashlib
from pathlib import Path
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from .config import settings

class DocumentProcessor:
    """Handles PDF loading and text processing"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def generate_document_id(self, file_path: Path) -> str:
        """Generate unique ID for a document based on its content"""
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash

    def load_pdf(self, file_path: Path) -> List[Document]:
        """Load and parse PDF document"""
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if not file_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF: {file_path}")

        loader = PyPDFLoader(str(file_path))
        documents = loader.load()

        if not documents:
            raise ValueError(f"No content found in PDF: {file_path}")

        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks"""
        return self.text_splitter.split_documents(documents)

    def process_pdf(self, file_path: Path) -> tuple[str, List[Document]]:
        """Complete PDF processing pipeline"""
        # Generate unique ID
        doc_id = self.generate_document_id(file_path)

        # Load and split documents
        raw_documents = self.load_pdf(file_path)
        processed_docs = self.split_documents(raw_documents)

        return doc_id, processed_docs

    def get_document_stats(self, documents: List[Document]) -> dict:
        """Get statistics about processed documents"""
        total_chars = sum(len(doc.page_content) for doc in documents)
        return {
            "total_chunks": len(documents),
            "total_characters": total_chars,
            "avg_chunk_size": total_chars // len(documents) if documents else 0
        }