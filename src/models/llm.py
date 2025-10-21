"""
Custom LLM implementation for local API integration
"""
import httpx
from typing import List, Optional, Any
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

from ..core.config import settings

class LocalAPILLM(LLM):
    """Custom LLM for consuming local API at localhost:11434"""

    model_name: str = settings.DEFAULT_MODEL
    api_url: str = settings.LOCAL_API_URL
    temperature: float = settings.LLM_TEMPERATURE
    max_tokens: int = settings.LLM_MAX_TOKENS

    @property
    def _llm_type(self) -> str:
        return "local_api"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Make a call to the local API"""
        try:
            # Prepare payload according to required format
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un asistente útil y conciso que responde en español."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            }

            # Make HTTP request
            with httpx.Client(timeout=settings.LLM_TIMEOUT) as client:
                response = client.post(
                    self.api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()

                # Parse response
                result = response.json()

                # Extract content from response
                if "message" in result and "content" in result["message"]:
                    return result["message"]["content"]
                else:
                    return "Error: Formato de respuesta inesperado"

        except httpx.RequestError as e:
            return f"Error de conexión: {str(e)}"
        except httpx.HTTPStatusError as e:
            return f"Error HTTP {e.response.status_code}: {e.response.text}"
        except Exception as e:
            return f"Error inesperado: {str(e)}"

    @property
    def _identifying_params(self) -> dict:
        """Get identifying parameters for the LLM"""
        return {
            "model_name": self.model_name,
            "api_url": self.api_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }