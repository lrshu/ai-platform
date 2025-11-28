# RAG Platform

A Retrieval-Augmented Generation (RAG) backend system for processing PDF documents and enabling intelligent search and question answering.

## Overview

The RAG Platform is a comprehensive system that enables:
- Document indexing and processing
- Intelligent search over document collections
- Conversational question answering with context awareness

## Features

### Document Processing
- PDF document parsing
- Text chunking for optimal retrieval
- Vector embedding generation
- Knowledge graph construction

### Search Capabilities
- Hybrid search (vector + graph-based)
- Query expansion and processing
- Result reranking and filtering
- Chunk content retrieval

### Conversational AI
- Context-aware question answering
- Conversation history management
- Follow-up question handling
- Response generation with LLM

## Architecture

The system is organized into the following components:

### Models
- `Document`: Represents a document with content and metadata
- `Chunk`: Represents a text chunk from a document
- `Vector`: Represents vector embeddings
- `KnowledgeGraph`: Represents document relationships
- `Query`: Represents user questions
- `SearchResult`: Represents retrieved document chunks
- `Conversation`: Manages conversation context
- `Response`: Represents generated answers

### Services
- `IndexingService`: Handles document processing and indexing
- `PreRetrievalService`: Processes queries before retrieval
- `RetrievalService`: Performs document retrieval
- `PostRetrievalService`: Processes search results
- `GenerationService`: Generates responses using LLM
- `OrchestrationService`: Coordinates the complete RAG pipeline

### Libraries
- `DatabaseConnection`: Memgraph/Neo4j connection management
- `LLMClient`: Qwen API client for embeddings and generation
- `PDFParser`: PDF document parsing
- `Chunker`: Text chunking functionality
- `VectorStore`: Vector storage operations
- `GraphStore`: Knowledge graph storage operations

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```bash
   QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_API_KEY=your_api_key_here
   DATABASE_URL=bolt://127.0.0.1:7687
   DATABASE_USER=your_username
   DATABASE_PASSWORD=your_password
   ```

## Usage

### CLI Application

Run the CLI application:
```bash
python main.py
```

Commands:
- `index <id> <name> <content>` - Index a document
- `search <collection> <question>` - Search for information
- `chat <collection> <question>` - Chat about documents
- `quit` - Exit the application

### Example Usage

```python
from src.lib.database import DatabaseConnection
from src.services.orchestration import OrchestrationService

# Initialize database connection
db = DatabaseConnection(uri="bolt://127.0.0.1:7687")
db.connect()

# Initialize orchestration service
orchestrator = OrchestrationService(db)

# Search for information
results, contents = orchestrator.search(
    name="my_collection",
    question="What is machine learning?",
    top_k=5
)

# Engage in conversation
response, conversation = orchestrator.chat(
    name="my_collection",
    question="What is machine learning?",
)
```

## Testing

Run tests:
```bash
pytest tests/
```

## License

MIT