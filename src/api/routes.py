"""
API route handlers for the Document Assistant
"""
import time
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from langchain.chains import RetrievalQA

from ..core import settings, DocumentProcessor, VectorStoreManager
from ..models import LocalAPILLM, QueryRequest, QueryResponse, UploadResponse, DocumentInfo, HealthResponse

router = APIRouter()

# Global instances (singletons)
document_processor = DocumentProcessor()
vector_store_manager = VectorStoreManager()
llm = LocalAPILLM()

def get_qa_chain(retriever):
    """Get or create QA chain with the provided retriever"""
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

@router.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Asistente de Documentos API",
        "description": "API REST para consultas inteligentes en documentos PDF",
        "features": {
            "free": "100% Gratuito - DeepSeek R1 + HuggingFace embeddings",
            "fast": "Súper Rápido - Caché inteligente y persistencia",
            "multi_doc": "Multi-documento - Múltiples PDFs simultáneamente",
            "private": "Privado - Todo procesado localmente"
        },
        "endpoints": {
            "docs": "/docs - Documentación interactiva",
            "upload": "POST /upload - Cargar documento PDF",
            "query": "POST /query - Realizar consulta",
            "documents": "GET /documents - Listar documentos",
            "health": "GET /health - Estado del sistema"
        }
    }

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    start_time = time.time()

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    try:
        # Save uploaded file temporarily
        temp_file_path = settings.UPLOAD_DIR / file.filename
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the document
        doc_id, processed_docs = document_processor.process_pdf(temp_file_path)

        # Check if already processed
        if vector_store_manager.document_exists(doc_id):
            processing_time = time.time() - start_time
            return UploadResponse(
                message=f"Documento ya existe en la base de datos",
                document_id=doc_id,
                filename=file.filename,
                chunks_created=len(processed_docs),
                processing_time=processing_time
            )

        # Create vector store
        vector_store_manager.create_vector_store(doc_id, processed_docs, file.filename)

        # Save the original file with doc_id prefix
        final_file_path = settings.UPLOAD_DIR / f"{doc_id}_{file.filename}"
        if temp_file_path != final_file_path:
            temp_file_path.rename(final_file_path)

        processing_time = time.time() - start_time

        return UploadResponse(
            message=f"Documento procesado exitosamente",
            document_id=doc_id,
            filename=file.filename,
            chunks_created=len(processed_docs),
            processing_time=processing_time
        )

    except Exception as e:
        # Clean up on error
        if temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the uploaded documents"""
    start_time = time.time()

    try:
        # Get available documents
        available_docs = vector_store_manager.list_documents()

        if not available_docs:
            raise HTTPException(status_code=404, detail="No hay documentos cargados")

        # Filter documents if specific IDs requested
        if request.doc_ids:
            target_docs = [doc for doc in available_docs if doc["id"] in request.doc_ids]
            if not target_docs:
                raise HTTPException(status_code=404, detail="Documentos especificados no encontrados")
            doc_ids = request.doc_ids
        else:
            doc_ids = [doc["id"] for doc in available_docs]

        # Get combined vector store
        vector_store = vector_store_manager.get_combined_vector_store(doc_ids)
        if vector_store is None:
            raise HTTPException(status_code=500, detail="Error cargando base de datos vectorial")

        # Create retriever
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})

        # Get QA chain with retriever
        qa = get_qa_chain(retriever)

        # Perform query
        result = qa.invoke({"query": request.question})

        # Extract answer and sources
        answer = result.get("result", "No se pudo obtener respuesta")
        source_docs = result.get("source_documents", [])

        # Get source filenames
        sources = []
        for source_doc in source_docs:
            if hasattr(source_doc, 'metadata') and 'source' in source_doc.metadata:
                source_path = Path(source_doc.metadata['source'])
                sources.append(source_path.name)

        processing_time = time.time() - start_time

        return QueryResponse(
            answer=answer,
            sources=list(set(sources)),  # Remove duplicates
            doc_count=len(doc_ids),
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error realizando consulta: {str(e)}")

@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all uploaded documents"""
    try:
        documents = vector_store_manager.list_documents()
        return [DocumentInfo(**doc) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando documentos: {str(e)}")

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a specific document"""
    try:
        # Delete vector store
        success = vector_store_manager.delete_vector_store(doc_id)

        if not success:
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        # Try to delete uploaded file
        for file_path in settings.UPLOAD_DIR.glob(f"{doc_id}_*"):
            try:
                file_path.unlink()
            except Exception:
                pass  # File might not exist or be in use

        return {"message": f"Documento {doc_id} eliminado exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando documento: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        documents = vector_store_manager.list_documents()

        return HealthResponse(
            status="healthy",
            features={
                "documents_loaded": len(documents),
                "vector_store": "FAISS",
                "embeddings": settings.EMBEDDING_MODEL,
                "llm_model": settings.DEFAULT_MODEL,
                "storage_dirs": {
                    "uploads": str(settings.UPLOAD_DIR),
                    "vector_dbs": str(settings.VECTOR_DB_DIR),
                    "cache": str(settings.CACHE_DIR)
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")