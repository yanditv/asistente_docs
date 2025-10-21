# Asistente de Documentos

Una aplicación completa para realizar consultas inteligentes en documentos PDF usando inteligencia artificial **100% gratuita**.

## 🎯 Características

- ✅ **100% Gratuito** - Usa DeepSeek R1 y HuggingFace embeddings
- 🚀 **Súper Rápido** - Caché inteligente y persistencia de embeddings
- 📚 **Multi-documento** - Carga y consulta múltiples PDFs simultáneamente
- 🔒 **Privado** - Todo se procesa localmente
- 🌐 **API REST** - Fácil integración con cualquier aplicación
- 📱 **Interfaz Web** - Cliente web incluido para uso inmediato

## 📁 Estructura del Proyecto

```
asistente_docs/
├── src/                          # Código fuente principal
│   ├── api/                      # FastAPI application
│   │   ├── app.py               # Configuración de la app
│   │   └── routes.py            # Endpoints de la API
│   ├── core/                    # Lógica de negocio central
│   │   ├── config.py            # Configuración global
│   │   ├── document_processor.py # Procesamiento de PDFs
│   │   └── vector_store.py      # Gestión de vectores
│   └── models/                  # Modelos y schemas
│       ├── llm.py              # Modelo LLM personalizado
│       └── schemas.py          # Schemas Pydantic
├── frontend/                    # Interfaz web
│   ├── web_client.html         # Cliente web principal
│   └── web_server.py           # Servidor web simple
├── scripts/                     # Scripts utilitarios
│   └── start_all.py            # Iniciador automático
├── docs/                       # Documentación
├── data/                       # Datos generados (ignorado en Git)
│   ├── uploads/                # PDFs subidos
│   ├── vector_dbs/             # Bases de datos vectoriales
│   └── cache/                  # Cache de metadatos
├── main.py                     # Punto de entrada principal
└── requirements.txt            # Dependencias
```

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación

**Opción A: Inicio automático (recomendado)**
```bash
python scripts/start_all.py
```

**Opción B: Solo API**
```bash
python main.py
```


### 3. Usar la interfaz web

- Automáticamente se abre en: http://localhost:3000/web_client.html
- O accede manualmente a la URL

### 4. Documentación de la API

- Documentación interactiva: http://localhost:8000/docs
- API REST: http://localhost:8000

## 📝 Uso de la API

### Cargar documento
```bash
curl -X POST "http://localhost:8000/upload" \\
  -F "file=@documento.pdf"
```

### Realizar consulta
```bash
curl -X POST "http://localhost:8000/query" \\
  -H "Content-Type: application/json" \\
  -d '{"question": "¿Cuál es el tema principal?"}'
```

### Listar documentos
```bash
curl "http://localhost:8000/documents"
```

## Configuración

La configuración se gestiona desde `src/core/config.py`:

- **Puertos**: API (8000), Web (3000)
- **Modelos**: LLM y embeddings
- **Directorios**: Datos y cache
- **Parámetros**: Chunks, temperatura, etc.

## Arquitectura

### Capas de la Aplicación

1. **API Layer** (`src/api/`): FastAPI routes y middleware
2. **Core Layer** (`src/core/`): Lógica de negocio y procesamiento
3. **Models Layer** (`src/models/`): Schemas y modelos de datos
4. **Frontend Layer** (`frontend/`): Interfaz web

### Flujo de Datos

1. **Upload**: PDF → DocumentProcessor → VectorStore → Cache
2. **Query**: Pregunta → VectorStore → LLM → Respuesta
3. **Storage**: Datos persistentes en `data/`

## Desarrollo

### Estructura Modular

- **Separación de responsabilidades**: Cada módulo tiene una función específica
- **Configuración centralizada**: Todo en `config.py`
- **Reutilización**: Componentes independientes y testeable
- **Escalabilidad**: Fácil agregar nuevas características

### Agregar Nuevas Funcionalidades

1. **Nuevo endpoint**: Agregar en `src/api/routes.py`
2. **Nueva lógica**: Crear en `src/core/`
3. **Nuevo modelo**: Definir en `src/models/schemas.py`
4. **Nueva configuración**: Añadir en `src/core/config.py`

## Scripts Disponibles

- `main.py`: Inicia solo la API REST
- `scripts/start_all.py`: Inicia API + interfaz web

## Dependencias Principales

- **FastAPI**: Framework web moderno
- **LangChain**: Framework para aplicaciones LLM
- **FAISS**: Base de datos vectorial
- **HuggingFace**: Embeddings gratuitos
- **sentence-transformers**: Modelos de embeddings

## Listo para usar

Tu asistente de documentos está completamente configurado y optimizado para consultas inteligentes súper rápidas y completamente gratuitas! 🚀

### Próximos pasos:

1. Sube tus documentos PDF
2. Realiza consultas inteligentes
3. Explora la API REST
4. Personaliza según tus necesidades