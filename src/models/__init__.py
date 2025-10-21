"""
Data models and schemas for the Document Assistant
"""
from .llm import LocalAPILLM
from .schemas import QueryRequest, QueryResponse, UploadResponse, DocumentInfo, HealthResponse, ErrorResponse

__all__ = ['LocalAPILLM', 'QueryRequest', 'QueryResponse', 'UploadResponse', 'DocumentInfo', 'HealthResponse', 'ErrorResponse']