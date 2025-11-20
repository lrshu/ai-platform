# RAG Backend Implementation

This project implements a Retrieval-Augmented Generation (RAG) backend system that follows the Modular RAG paradigm with six standardized pipeline stages. The system provides document indexing, search and retrieval capabilities, and answer generation using Qwen models and Memgraph for storage.

## Features

- Document parsing and indexing with Small-to-Big chunking strategy
- Vector and keyword search capabilities using Memgraph
- Text generation and embedding using Qwen models via DashScope
- Graph-based entity extraction and relationship storage
- RESTful API for indexing and search operations
- Configuration-driven architecture with environment variable overrides

## Prerequisites

- Python 3.12+
- Memgraph database instance
- DashScope API key for Qwen models
- Access to Mineru document parsing service

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-platform
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Create a `config.json5` file based on the example:
   ```json5
   {
     "database": {
       "uri": "bolt://localhost:7687",
       "user": "memgraph",
       "password": "password"
     },
     "pipeline_capabilities": {
       "embedder": {
         "provider": "Qwen",
         "name": "text-embedding-v4"
       },
       "generator": {
         "provider": "Qwen",
         "name": "qwen-plus"
       },
       "reranker": {
         "provider": "Qwen",
         "name": "gte-rerank"
       },
       "parser": {
         "provider": "Mineru",
         "name": "v1"
       }
     },
     "provider_map": {
       "Qwen": "app.providers.qwen_provider.QwenProvider",
       "Mineru": "app.providers.mineru_provider.MineruProvider"
     }
   }
   ```

4. Set environment variables:
   ```bash
   export DASHSCOPE_API_KEY=your_api_key_here
   export MEMGRAPH_PASSWORD=your_password_here
   ```

## Running the Service

1. Start Memgraph database (follow Memgraph documentation)

2. Run the FastAPI application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

- `POST /api/rag/indexing` - Trigger document indexing
- `GET /health` - Health check endpoint

## Project Structure

```
app/
├── api/                 # API Gateway & Endpoints
├── common/              # Core Infrastructure
│   ├── interfaces/      # Abstract Base Classes
│   ├── models.py        # Shared Pydantic Models
│   ├── config_loader.py # Configuration Management
│   ├── factory.py       # Provider Factory
├── database/            # Memgraph Implementation
├── indexing/            # Indexing Logic
├── retrieval/           # Retrieval Logic (Pre & Core)
├── post_retrieval/      # Post-Retrieval Logic
├── generation/          # Generation Logic
├── providers/           # External Service Providers
├── orchestration/       # Pipeline & Orchestrator
tests/
├── contract/
├── integration/
└── unit/
```

## Development

### Linting and Formatting

```bash
# Run linter
ruff check .

# Format code
black .
```

### Testing

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/
```
