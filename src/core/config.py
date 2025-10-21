"""
Configuration settings for the Document Assistant
"""
import os
from pathlib import Path
from typing import Dict, Any

# Environment setup
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

class Settings:
    """Application settings and configuration"""

    # API Configuration
    LOCAL_API_URL: str = "http://localhost:11434/api/chat"
    DEFAULT_MODEL: str = "gpt-oss:20b"

    # Server Configuration
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    WEB_SERVER_PORT: int = 3000

    # Directory Configuration
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = PROJECT_ROOT / "data" / "uploads"
    VECTOR_DB_DIR: Path = PROJECT_ROOT / "data" / "vector_dbs"
    CACHE_DIR: Path = PROJECT_ROOT / "data" / "cache"

    # Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200

    # LLM Configuration
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 1500
    LLM_TIMEOUT: float = 60.0

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        for dir_path in [cls.UPLOAD_DIR, cls.VECTOR_DB_DIR, cls.CACHE_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_settings_dict(cls) -> Dict[str, Any]:
        """Get all settings as a dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and not callable(getattr(cls, key))
        }

# Global settings instance
settings = Settings()

# Create directories on import
settings.create_directories()