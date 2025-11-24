# RAG Backend System Architecture

## Overview

The RAG (Retrieval-Augmented Generation) Backend System is designed to provide document indexing, hybrid search capabilities, and conversational question answering through a command-line interface. The system combines vector similarity search with knowledge graph relationships to provide accurate and contextually relevant answers to user queries.

## System Components

### 1. Core Services

#### Indexing Service
- **PDF Parser**: Extracts text content from PDF documents
- **Document Chunker**: Splits documents into manageable chunks
- **Embedding Generator**: Creates vector embeddings for document chunks
- **Knowledge Graph Extractor**: Identifies entities and relationships in text

#### Search Service
- **Query Expander**: Enhances queries with related terms
- **Vector Search**: Performs similarity search using embeddings
- **Graph Search**: Finds relevant content using knowledge graph relationships
- **Retrieval Service**: Combines search methods and re-ranks results

#### Chat Service
- **Conversation Manager**: Maintains chat session context
- **Answer Generator**: Creates natural language responses using LLM
- **Chat Orchestration**: Coordinates the chat workflow

### 2. Data Models

#### Document Management
- **DocumentCollection**: Groups related documents
- **Document**: Represents an indexed document
- **DocumentChunk**: Segments of document text

#### Search and Retrieval
- **Query**: User search queries
- **VectorEmbedding**: Numerical representations of text
- **RetrievalResult**: Search results with relevance scores

#### Knowledge Graph
- **KnowledgeGraphNode**: Extracted entities
- **KnowledgeGraphRelationship**: Relationships between entities

#### Conversation
- **ConversationContext**: Chat session history

### 3. External Integrations

#### Qwen API
- **Embedding Generation**: Text embedding service
- **Language Model**: Answer generation service
- **Re-ranking**: Result re-ranking service

#### Memgraph Database
- **Vector Storage**: Stores document embeddings
- **Knowledge Graph**: Maintains entity relationships
- **Metadata Storage**: Document and collection information

## Data Flow

### Document Indexing Pipeline
1. User submits PDF document for indexing
2. PDF Parser extracts text content
3. Document Chunker splits text into chunks
4. Embedding Generator creates vector embeddings
5. Knowledge Graph Extractor identifies entities/relationships
6. All data stored in Memgraph database

### Search Pipeline
1. User submits search query
2. Query Expander enhances the query
3. Vector Search finds similar document chunks
4. Graph Search finds related entities
5. Retrieval Service combines and re-ranks results
6. Results returned to user

### Chat Pipeline
1. User submits question in chat session
2. Conversation Manager retrieves session history
3. Retrieval Service finds relevant document content
4. Answer Generator creates response using LLM
5. Conversation Manager stores interaction
6. Response returned to user

## Technology Stack

### Core Technologies
- **Language**: Python 3.12+
- **Framework**: LangChain Core
- **Database**: Memgraph (Neo4j driver)
- **LLM**: Qwen3-Max
- **Embeddings**: Qwen text-embedding-v4
- **Re-ranking**: DashScopeRerank

### Development Tools
- **Package Manager**: uv
- **Testing**: pytest
- **Linting**: ruff
- **Documentation**: Markdown

## Performance Considerations

### Scalability
- Database connection pooling
- Concurrent request handling
- Efficient vector similarity search

### Optimization
- Caching of frequently accessed embeddings
- Batch processing for large documents
- Memory-efficient chunking strategies

## Security

### Data Protection
- Environment variable configuration
- Secure API key handling
- Input validation and sanitization

### Access Control
- Document collection isolation
- Session-based conversation management
- Rate limiting for API endpoints

## Deployment

### Requirements
- Python 3.12+
- Memgraph database
- DashScope API access
- PDF processing libraries

### Configuration
- Environment variables for API keys
- Database connection settings
- Performance tuning parameters

## Testing Strategy

### Unit Tests
- Individual service functionality
- Model validation
- Utility functions

### Integration Tests
- End-to-end workflows
- Database interactions
- API integrations

### Performance Tests
- Response time measurements
- Concurrent user simulation
- Memory usage monitoring