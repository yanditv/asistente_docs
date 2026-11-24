"""
Vector store management for document embeddings
"""
import pickle
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from .config import settings

class VectorStoreManager:
    """Manages FAISS vector stores and embeddings"""

    def __init__(self):
        self.embeddings = None
        self._metadata_cache = {}
        self._load_metadata()

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get or create embeddings model (singleton pattern)"""
        if self.embeddings is None:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        return self.embeddings

    def _get_vector_db_path(self, doc_id: str) -> Path:
        """Get the path for a document's vector database"""
        return settings.VECTOR_DB_DIR / doc_id

    def _get_metadata_path(self) -> Path:
        """Get the path for metadata cache"""
        return settings.CACHE_DIR / "metadata.pkl"

    def _load_metadata(self) -> None:
        """Load metadata cache from disk"""
        metadata_path = self._get_metadata_path()
        if metadata_path.exists():
            try:
                with open(metadata_path, 'rb') as f:
                    self._metadata_cache = pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not load metadata cache: {e}")
                self._metadata_cache = {}

    def _save_metadata(self) -> None:
        """Save metadata cache to disk"""
        metadata_path = self._get_metadata_path()
        try:
            with open(metadata_path, 'wb') as f:
                pickle.dump(self._metadata_cache, f)
        except Exception as e:
            print(f"Warning: Could not save metadata cache: {e}")

    def document_exists(self, doc_id: str) -> bool:
        """Check if a document's vector store already exists"""
        return self._get_vector_db_path(doc_id).exists()

    def create_vector_store(self, doc_id: str, documents: List[Document], filename: str, folder: Optional[str] = None) -> FAISS:
        """Create and save a new vector store for documents"""
        embeddings = self.get_embeddings()

        # Create vector store
        vector_store = FAISS.from_documents(documents, embeddings)

        # Save to disk
        vector_store.save_local(str(self._get_vector_db_path(doc_id)))

        # Update metadata
        self._metadata_cache[doc_id] = {
            "filename": filename,
            "folder": folder,
            "created_at": datetime.now().isoformat(),
            "num_chunks": len(documents),
            "total_chars": sum(len(doc.page_content) for doc in documents)
        }
        self._save_metadata()

        return vector_store

    def load_vector_store(self, doc_id: str) -> Optional[FAISS]:
        """Load an existing vector store"""
        vector_db_path = self._get_vector_db_path(doc_id)

        if not vector_db_path.exists():
            return None

        try:
            embeddings = self.get_embeddings()
            return FAISS.load_local(str(vector_db_path), embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            print(f"Error loading vector store for {doc_id}: {e}")
            return None

    def get_combined_vector_store(self, doc_ids: List[str]) -> Optional[FAISS]:
        """Combine multiple vector stores into one"""
        if not doc_ids:
            return None

        # Load first vector store
        combined_store = self.load_vector_store(doc_ids[0])
        if combined_store is None:
            return None

        # Merge additional stores
        for doc_id in doc_ids[1:]:
            store = self.load_vector_store(doc_id)
            if store is not None:
                combined_store.merge_from(store)

        return combined_store

    def delete_vector_store(self, doc_id: str) -> bool:
        """Delete a vector store and its metadata"""
        vector_db_path = self._get_vector_db_path(doc_id)

        try:
            # Remove directory and all files
            if vector_db_path.exists():
                import shutil
                shutil.rmtree(vector_db_path)

            # Remove from metadata
            if doc_id in self._metadata_cache:
                del self._metadata_cache[doc_id]
                self._save_metadata()

            return True
        except Exception as e:
            print(f"Error deleting vector store {doc_id}: {e}")
            return False

    def list_documents(self) -> List[Dict]:
        """List all documents with their metadata"""
        result = []
        for doc_id, metadata in self._metadata_cache.items():
            result.append({
                "id": doc_id,
                "filename": metadata.get("filename", "Unknown"),
                "folder": metadata.get("folder"),
                "created_at": metadata.get("created_at", "Unknown"),
                "num_chunks": metadata.get("num_chunks", 0),
                "total_chars": metadata.get("total_chars", 0),
                "exists": self.document_exists(doc_id)
            })
        return sorted(result, key=lambda x: x.get("created_at", ""), reverse=True)

    def set_folder(self, doc_id: str, folder: Optional[str]) -> None:
        """Move an already indexed document into a folder (re-uploads keep the latest folder)"""
        if doc_id in self._metadata_cache and folder:
            self._metadata_cache[doc_id]["folder"] = folder
            self._save_metadata()

    def get_document_metadata(self, doc_id: str) -> Optional[Dict]:
        """Get metadata for a specific document"""
        return self._metadata_cache.get(doc_id)