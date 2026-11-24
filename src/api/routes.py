"""
API route handlers for the Document Assistant

Endpoints are plain `def` on purpose: FastAPI runs them in a threadpool, so the
blocking work (PDF parsing, embeddings, LLM calls) never stalls the event loop.
"""
import os
import time
import shutil
import threading
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from ..core import settings, DocumentProcessor, VectorStoreManager
from ..models import QueryRequest, QueryResponse, Citation, UploadResponse, DocumentInfo, HealthResponse

router = APIRouter()

# Global instances (singletons)
document_processor = DocumentProcessor()
vector_store_manager = VectorStoreManager()
_llm = None

# Warm the embedding model in the background so the first query isn't ~40s slower
threading.Thread(target=vector_store_manager.get_embeddings, daemon=True).start()

QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""Eres un asistente que responde preguntas usando solo los fragmentos de documentos dados.
Responde en español, de forma clara y concisa. Usa markdown (listas, **negritas**) cuando ayude.
Si la respuesta no está en los fragmentos, dilo sin inventar nada.

Fragmentos:
{context}

Pregunta: {question}

Respuesta:""",
)

FRONTEND_FILE = settings.PROJECT_ROOT / "frontend" / "index.html"


def llm_ready() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def get_llm() -> ChatOpenAI:
    """Create the LLM lazily so the API boots (and the UI explains) without a key"""
    global _llm
    if not llm_ready():
        raise HTTPException(
            status_code=503,
            detail="Falta OPENAI_API_KEY. Añádela al archivo .env y reinicia el servidor.",
        )
    if _llm is None:
        _llm = ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            timeout=settings.LLM_TIMEOUT,
        )
    return _llm


@router.get("/", include_in_schema=False)
def index():
    """Serve the web interface"""
    return FileResponse(FRONTEND_FILE)


@router.post("/upload", response_model=UploadResponse)
def upload_document(file: UploadFile = File(...), folder: Optional[str] = Form(None)):
    """Upload and process a PDF document, optionally tagging the folder it came from"""
    start_time = time.time()

    # Strip any path components from the client-supplied name (path traversal)
    filename = Path(file.filename or "").name
    if not filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    folder = (folder or "").strip()[:120] or None

    temp_file_path = settings.UPLOAD_DIR / filename
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Hash first: re-importing a folder skips parsing files already indexed
        doc_id = document_processor.generate_document_id(temp_file_path)
        if vector_store_manager.document_exists(doc_id):
            vector_store_manager.set_folder(doc_id, folder)
            meta = vector_store_manager.get_document_metadata(doc_id) or {}
            return UploadResponse(
                message="El documento ya estaba cargado",
                document_id=doc_id,
                filename=filename,
                chunks_created=meta.get("num_chunks", 0),
                processing_time=time.time() - start_time,
            )

        _, processed_docs = document_processor.process_pdf(temp_file_path)
        if not processed_docs:
            raise ValueError("El PDF no contiene texto extraíble (¿es un escaneo?)")

        vector_store_manager.create_vector_store(doc_id, processed_docs, filename, folder)
        temp_file_path.rename(settings.UPLOAD_DIR / f"{doc_id}_{filename}")

        return UploadResponse(
            message="Documento procesado",
            document_id=doc_id,
            filename=filename,
            chunks_created=len(processed_docs),
            processing_time=time.time() - start_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando documento: {e}")
    finally:
        if temp_file_path.exists():
            temp_file_path.unlink()


@router.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    """Query the uploaded documents"""
    start_time = time.time()
    llm = get_llm()

    available_ids = {doc["id"] for doc in vector_store_manager.list_documents()}
    if not available_ids:
        raise HTTPException(status_code=404, detail="Todavía no hay documentos cargados")

    doc_ids = [d for d in request.doc_ids if d in available_ids] if request.doc_ids else list(available_ids)
    if not doc_ids:
        raise HTTPException(status_code=404, detail="Los documentos seleccionados ya no existen")

    vector_store = vector_store_manager.get_combined_vector_store(doc_ids)
    if vector_store is None:
        raise HTTPException(status_code=500, detail="Error cargando la base de datos vectorial")

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 8}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_PROMPT},
    )

    try:
        result = qa.invoke({"query": request.question})
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error del modelo: {e}")

    citations, seen = [], set()
    for doc in result.get("source_documents", []):
        name = Path(doc.metadata.get("source", "")).name
        page = doc.metadata.get("page")
        page = page + 1 if isinstance(page, int) else None  # PyPDF pages are 0-based
        if (name, page) in seen:
            continue
        seen.add((name, page))
        snippet = " ".join(doc.page_content.split())
        citations.append(Citation(filename=name, page=page, snippet=snippet[:400] + ("…" if len(snippet) > 400 else "")))

    return QueryResponse(
        answer=result.get("result", "No se pudo obtener respuesta"),
        sources=sorted({c.filename for c in citations}),
        citations=citations,
        doc_count=len(doc_ids),
        processing_time=time.time() - start_time,
    )


@router.get("/documents", response_model=List[DocumentInfo])
def list_documents():
    """List all uploaded documents"""
    return [DocumentInfo(**doc) for doc in vector_store_manager.list_documents()]


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    """Delete a specific document"""
    if doc_id not in {doc["id"] for doc in vector_store_manager.list_documents()}:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if not vector_store_manager.delete_vector_store(doc_id):
        raise HTTPException(status_code=500, detail="No se pudo eliminar el documento")

    for file_path in settings.UPLOAD_DIR.glob(f"{doc_id}_*"):
        file_path.unlink(missing_ok=True)

    return {"message": "Documento eliminado"}


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        features={
            "documents_loaded": len(vector_store_manager.list_documents()),
            "llm_ready": llm_ready(),
            "llm_model": settings.DEFAULT_MODEL,
            "embeddings": settings.EMBEDDING_MODEL,
            "vector_store": "FAISS",
        },
    )
