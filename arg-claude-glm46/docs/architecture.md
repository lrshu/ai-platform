# System Architecture

## Overview

The RAG Backend System follows a modular, service-oriented architecture designed for scalability and maintainability. The system is divided into distinct layers that handle different aspects of the RAG pipeline.

## Architecture Layers

### 1. Presentation Layer (CLI)

The Command Line Interface provides the entry point for all system interactions:
- `indexing`: Document ingestion and processing
- `search`: Information retrieval from indexed documents
- `chat`: Conversational question answering

### 2. Orchestration Layer

High-level coordination services that manage complex workflows:
- `IndexingOrchestrator`: Coordinates the complete document indexing pipeline
- `SearchOrchestrator`: Manages the search workflow including query expansion and result re-ranking
- `ConversationManager`: Handles conversational context and session management

### 3. Service Layer

Specialized services that implement core functionality:

#### Indexing Services
- `DocumentParser`: Extracts content from PDF documents
- `Chunker`: Splits documents into searchable chunks
- `Embedder`: Generates vector embeddings for content chunks
- `KGExtractor`: Identifies entities and relationships for knowledge graph construction
- `StorageService`: Manages data persistence

#### Retrieval Services
- `QueryExpander`: Enhances search queries for better recall
- `VectorSearchService`: Performs similarity search using embeddings
- `GraphSearchService`: Leverages knowledge graph relationships
- `HybridSearchOrchestrator`: Combines vector and graph search results
- `Reranker`: Improves result relevance using LLM-based scoring

#### Generation Services
- `PromptAssembler`: Constructs prompts for LLM interactions
- `LLMClientService`: Interfaces with language model APIs
- `AnswerGenerator`: Produces final responses to user queries

### 4. Model Layer

Data models that represent core domain concepts:
- `Document`: Represents indexed documents
- `Chunk`: Individual pieces of document content
- `Entity`/`Relationship`: Knowledge graph components
- `Query`: User search queries
- `SearchResult`: Retrieved information
- `Conversation`/`ConversationTurn`: Chat session data

### 5. Infrastructure Layer

Shared utilities and external integrations:
- `Database`: Memgraph connection and operations
- `Logging`: Structured logging with context
- `Metrics`: Performance monitoring and collection
- `LLM Client`: DashScope API integration

## Data Flow

### Indexing Pipeline

```
PDF Document → Parser → Chunker → Embedder → KG Extractor → Storage
```

1. **Parse**: Extract text content from PDF
2. **Chunk**: Split content into manageable pieces
3. **Embed**: Generate vector representations
4. **Extract**: Identify entities and relationships
5. **Store**: Persist all data in Memgraph

### Search Pipeline

```
Query → Expansion → Hybrid Search → Re-ranking → Results
```

1. **Expand**: Enhance query for better recall
2. **Search**: Perform vector and graph-based retrieval
3. **Combine**: Merge and rank results
4. **Re-rank**: Improve relevance with LLM scoring
5. **Return**: Provide final ranked results

### Conversation Pipeline

```
User Message → Context Management → Search → Response Generation → Chat History
```

1. **Context**: Maintain conversation state
2. **Retrieve**: Find relevant document content
3. **Generate**: Create context-aware responses
4. **Update**: Store conversation history

## Performance Considerations

### Caching

- Embedding results are cached to avoid recomputation
- Frequently accessed data is cached in memory
- Database query results are cached where appropriate

### Parallelization

- Document chunking and embedding generation are parallelized
- Search operations can be distributed across multiple workers
- Conversation sessions are isolated for concurrent access

### Monitoring

- Performance metrics are collected for all major operations
- Error rates and response times are tracked
- Resource utilization is monitored

## Scalability

### Horizontal Scaling

- Services can be deployed across multiple instances
- Database can be scaled independently
- Load balancing can distribute requests

### Vertical Scaling

- Individual services can be optimized for specific workloads
- Database queries can be optimized for performance
- Memory and CPU resources can be allocated as needed

## Security

### Data Protection

- Sensitive data is encrypted at rest
- API keys and credentials are managed securely
- Access controls are implemented at the service level

### Input Validation

- All user inputs are validated and sanitized
- File uploads are checked for malicious content
- Query parameters are validated before processing

## Reliability

### Error Handling

- Comprehensive exception handling throughout the system
- Graceful degradation when services are unavailable
- Detailed logging for debugging and monitoring

### Backup and Recovery

- Regular database backups are performed
- Recovery procedures are documented and tested
- Data integrity checks are implemented

## Deployment

### Containerization

- Services can be containerized using Docker
- Kubernetes can orchestrate container deployment
- Configuration is managed through environment variables

### CI/CD

- Automated testing ensures code quality
- Continuous integration builds and tests changes
- Deployment pipelines automate release processes