# Quickstart Guide: RAG Backend

## Prerequisites

1. Python 3.12+
2. uv package manager
3. Memgraph database instance
4. DashScope API key for Qwen models
5. Access to Mineru document parsing service

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-platform
   ```

2. Install dependencies using uv:
   ```bash
   uv init
   uv add fastapi pydantic gqlalchemy dashscope
   ```

3. Create a `config.json5` file based on the example in the specification:
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

4. Set environment variables for sensitive data:
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

## Indexing Documents

To index documents, make a POST request to the indexing endpoint:

```bash
curl -X POST http://localhost:8000/api/rag/indexing \
  -H "Content-Type: application/json" \
  -d '{
    "document_urls": ["http://example.com/document.pdf"],
    "collection_name": "my_collection"
  }'
```

## Searching and Generating Answers

To search documents and generate answers, make a POST request to the search endpoint:

```bash
curl -X POST http://localhost:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key features of the RAG backend?",
    "use_hyde": true,
    "use_rerank": true,
    "top_k": 5
  }'
```

The response will be streamed as Server-Sent Events (SSE) with generated tokens.

## Project Structure

The RAG backend follows a modular architecture with these key directories:

- `app/common/`: Shared interfaces, models, and utilities
- `app/providers/`: External service implementations
- `app/database/`: Memgraph database integration
- `app/indexing/`: Document parsing and indexing logic
- `app/retrieval/`: Search and retrieval modules
- `app/post_retrieval/`: Result processing and reranking
- `app/generation/`: LLM response generation
- `app/orchestration/`: Pipeline coordination
- `app/api/`: REST API endpoints

## Configuration

The system uses a configuration-driven approach:

1. Base configuration is loaded from `config.json5`
2. Sensitive values can be overridden with environment variables
3. Provider implementations are dynamically loaded based on configuration
4. Pipeline behavior is controlled by request parameters

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Different test types are organized in:
- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests for module interactions
- `tests/contract/`: Contract tests for API endpoints