"""
FastAPI application factory and configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from ..core.config import settings

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""

    app = FastAPI(
        title="Asistente de Documentos API",
        description="""
        Una API REST completa para cargar documentos PDF y realizar consultas inteligentes.

        - Embeddings locales (HuggingFace) e índice FAISS persistente en disco
        - Respuestas generadas con la API de OpenAI, con citas por página
        - Interfaz web en `/`
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(router)

    return app