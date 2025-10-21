"""
Core modules for the Document Assistant
"""
from .config import settings
from .document_processor import DocumentProcessor
from .vector_store import VectorStoreManager

__all__ = ['settings', 'DocumentProcessor', 'VectorStoreManager']