# Asistente de Documentos

Sube PDFs y hazles preguntas. Las respuestas salen solo de tus documentos e indican el archivo y la página de donde vienen.

- **Embeddings locales** (HuggingFace `all-MiniLM-L6-v2`) e índice **FAISS** guardado en disco: cada PDF se indexa una sola vez.
- **Respuestas con la API de OpenAI** (por defecto `gpt-4o-mini`).
- **Interfaz web** servida por la misma API en http://localhost:8000.

## Inicio rápido

Requiere Python 3.11 (langchain 0.1 no es compatible con Python 3.12.4+).

```bash
uv venv -p 3.11 .venv
uv pip install -p .venv -r requirements.txt

cp .env.example .env          # y pon tu OPENAI_API_KEY
.venv/bin/python main.py
```

Abre http://localhost:8000. La primera subida descarga el modelo de embeddings (~90 MB).

Sin clave la app arranca igual: puedes subir documentos y la interfaz te avisa de que falta la clave.

## Configuración (`.env`)

| Variable | Por defecto | Uso |
|---|---|---|
| `OPENAI_API_KEY` | — | Obligatoria para preguntar |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo de chat de OpenAI |

El resto (tamaño de fragmento, puertos, rutas) está en `src/core/config.py`.

## API

Documentación interactiva en http://localhost:8000/docs.

| Método | Ruta | Qué hace |
|---|---|---|
| `POST` | `/upload` | Sube e indexa un PDF (`multipart`, campo `file`) |
| `POST` | `/query` | `{"question": "...", "doc_ids": [..] \| null}` → respuesta + citas con página |
| `GET` | `/documents` | Lista los documentos indexados |
| `DELETE` | `/documents/{id}` | Elimina un documento y su índice |
| `GET` | `/health` | Estado, modelo y si la clave está configurada |

```bash
curl -F "file=@contrato.pdf" localhost:8000/upload
curl -H 'Content-Type: application/json' -d '{"question":"¿Cuál es el plazo?"}' localhost:8000/query
```

## Estructura

```
main.py                     arranca uvicorn
frontend/index.html         interfaz web (HTML + CSS + JS, sin build)
src/api/                    FastAPI: app y rutas
src/core/                   configuración, procesado de PDF, gestión de FAISS
src/models/                 schemas Pydantic; llm.py = cliente Ollama alternativo
data/                       subidas, índices y metadatos (ignorado en git)
```

Para volver a un modelo local, `src/models/llm.py` tiene un cliente para Ollama (`localhost:11434`); basta con usarlo en `get_llm()` de `src/api/routes.py`.
