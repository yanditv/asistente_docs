"""
Pydantic schemas for API requests and responses
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """Request schema for document queries"""
    question: str = Field(..., min_length=1, description="The question to ask about the documents")
    doc_ids: Optional[List[str]] = Field(None, description="Specific document IDs to query (if None, query all)")

class QueryResponse(BaseModel):
    """Response schema for document queries"""
    answer: str = Field(..., description="The answer to the question")
    sources: List[str] = Field(default_factory=list, description="Source documents used")
    doc_count: int = Field(..., description="Number of documents searched")
    processing_time: float = Field(..., description="Time taken to process the query in seconds")

class UploadResponse(BaseModel):
    """Response schema for document uploads"""
    message: str = Field(..., description="Success message")
    document_id: str = Field(..., description="Unique identifier for the uploaded document")
    filename: str = Field(..., description="Original filename")
    chunks_created: int = Field(..., description="Number of text chunks created")
    processing_time: float = Field(..., description="Time taken to process the document in seconds")

class DocumentInfo(BaseModel):
    """Schema for document information"""
    id: str = Field(..., description="Document unique identifier")
    filename: str = Field(..., description="Original filename")
    created_at: str = Field(..., description="ISO timestamp when document was processed")
    num_chunks: int = Field(..., description="Number of text chunks")
    total_chars: int = Field(..., description="Total character count")
    exists: bool = Field(..., description="Whether the vector store exists on disk")

class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")
    features: Dict[str, Any] = Field(default_factory=dict, description="Available features")

class ErrorResponse(BaseModel):
    """Response schema for errors"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")