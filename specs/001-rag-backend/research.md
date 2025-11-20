# Research Findings: RAG Backend Implementation

## 1. Memgraph Integration with Python

**Decision**: Use gqlalchemy library for Memgraph integration
**Rationale**: gqlalchemy is the official Python library for Memgraph that provides both ORM-like functionality and direct Cypher query execution. It supports both Bolt driver connections and additional features like graph algorithms through MAGE.
**Alternatives considered**:
- Direct Bolt driver: More low-level but requires more boilerplate code
- Neo4j Python driver: Compatible but misses Memgraph-specific features

## 2. DashScope SDK Usage for Qwen Models

**Decision**: Use dashscope Python SDK for all Qwen model interactions
**Rationale**: The dashscope SDK provides official support for all Qwen models including text generation, embeddings, and reranking. It handles authentication, request/response formatting, and error handling.
**Alternatives considered**:
- Direct REST API calls: More control but requires implementing authentication and error handling
- OpenAI-compatible API: Not directly compatible with DashScope

## 3. Mineru API Integration for Document Parsing

**Decision**: Use Mineru's Python library or REST API for document parsing
**Rationale**: Mineru is specifically designed for complex document parsing and provides high-quality results for PDFs and other document formats. Integration can be done through their Python package or REST API.
**Alternatives considered**:
- PyPDF2/PDFMiner: Good for simple PDF parsing but less capable with complex layouts
- Apache Tika: More general but larger dependency

## 4. FastAPI Implementation Patterns for Streaming Responses

**Decision**: Use StreamingResponse with async generators for SSE streaming
**Rationale**: FastAPI's StreamingResponse with async generators provides efficient, memory-friendly streaming of tokens as they're generated. This approach works well with async/await patterns.
**Alternatives considered**:
- WebSocket: More complex for simple streaming use cases
- Regular Response: Doesn't support real-time token streaming

## 5. Vector Search Implementation with Memgraph MAGE

**Decision**: Use Memgraph's MAGE library for vector similarity search
**Rationale**: MAGE provides optimized vector search algorithms that integrate directly with Memgraph's graph database, allowing for hybrid search combining vectors with graph relationships.
**Alternatives considered**:
- Separate vector database (Pinecone, Weaviate): Adds complexity with data synchronization
- Approximate algorithms: MAGE provides these out of the box

## 6. Configuration Management with JSON5 and Environment Variables

**Decision**: Use json5 library for parsing config.json5 with python-dotenv for environment variables
**Rationale**: json5 library allows parsing JSON5 files with comments and trailing commas. python-dotenv handles environment variable loading from .env files, with environment variables overriding config values.
**Alternatives considered**:
- Standard json library: Doesn't support comments
- Custom parser: Unnecessary complexity

## 7. Small-to-Big Chunking Strategy Implementation

**Decision**: Implement recursive character text splitting with overlap
**Rationale**: Split documents into parent chunks (~1000 tokens) and child chunks (~200 tokens) with overlap to maintain context. This approach balances retrieval granularity with context preservation.
**Alternatives considered**:
- Fixed-size splitting: May break sentences/paragraphs
- Semantic splitting: More complex, requires additional processing

## 8. HyDE (Hypothetical Document Embeddings) Implementation

**Decision**: Generate hypothetical answers using LLM and use their embeddings for search
**Rationale**: HyDE improves retrieval by generating documents similar to what should be returned, which works well with vector search. Implementation involves prompting the LLM to generate an answer and then embedding that answer.
**Alternatives considered**:
- Query expansion: Good but doesn't change the embedding space
- Multi-query: Generates multiple queries but still uses original query embedding

## 9. Graph Entity Extraction Patterns

**Decision**: Use LLM prompting with structured output format for entity extraction
**Rationale**: Prompt the LLM to extract entities and relationships in a structured format (JSON) that can be directly converted to graph nodes and edges. This approach leverages the LLM's understanding while ensuring consistent output.
**Alternatives considered**:
- NER libraries (spaCy): Good for standard entities but less flexible
- Rule-based extraction: Limited to predefined patterns

## 10. Dependency Injection Patterns in Python

**Decision**: Use factory pattern with configuration-driven instantiation
**Rationale**: Create factory classes that read configuration and instantiate the appropriate provider implementations. This approach is simple, testable, and follows the configuration-driven architecture principle.
**Alternatives considered**:
- Third-party DI frameworks (dependency-injector): Adds dependency but provides more features
- Manual instantiation: Less flexible and harder to configure

## 11. Docker Containerization for Python 3.12 and uv

**Decision**: Use official Python 3.12 base image with uv installed
**Rationale**: Python 3.12 provides the latest features and performance improvements. Installing uv in the container provides fast dependency management while maintaining compatibility with standard pip workflows.
**Alternatives considered**:
- Using uv's base images: May not be as stable or well-maintained
- Standard pip: Slower dependency installation

## 12. Streaming Server-Sent Events (SSE) Implementation

**Decision**: Use FastAPI's StreamingResponse with async generators
**Rationale**: FastAPI has built-in support for StreamingResponse which works well with async/await patterns. This approach is efficient and memory-friendly, streaming tokens as they're generated.
**Alternatives considered**:
- WebSocket: More complex for simple streaming use cases
- Polling: Inefficient and introduces latency