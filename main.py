#!/usr/bin/env python3
"""
Document Assistant - Main Entry Point
Fast startup script for the Document Assistant API server
"""

import uvicorn
from src.api import create_app
from src.core.config import settings

def main():
    """Main entry point for the application"""
    print("Iniciando Asistente de Documentos...")
    print(f"Interfaz web: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"Documentación en: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print()

    # Create and run the FastAPI app
    app = create_app()

    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()