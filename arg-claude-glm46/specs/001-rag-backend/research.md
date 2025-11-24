# Research Findings: RAG Backend Implementation

## 1. PDF Parsing and Content Extraction

**Decision**: Use PyMuPDF (fitz) for PDF parsing
**Rationale**: PyMuPDF is a lightweight, fast PDF processing library that can extract text and images efficiently. It's well-maintained and has good performance characteristics.
**Alternatives considered**:
- pdfminer.six: More complex API, slower performance
- PyPDF2: Limited functionality for complex PDFs
- pdfplumber: Good for tables but overkill for our use case

## 2. Document Chunking Strategy

**Decision**: Use LangChain's text splitters with semantic chunking
**Rationale**: LangChain provides robust text splitting capabilities that can handle various document structures. Semantic chunking ensures that chunks maintain contextual coherence.
**Alternatives considered**:
- Fixed-size chunking: Simple but can break up related content
- Sentence-based chunking: Better than fixed-size but doesn't consider semantic boundaries
- Custom recursive chunking: More complex to implement and maintain

## 3. Vector Embedding Generation

**Decision**: Use DashScope's Qwen text-embedding-v4 API
**Rationale**: As specified in the requirements, this is the designated embedding model. Using the API service avoids local model deployment complexity.
**Alternatives considered**:
- SentenceTransformers locally: Requires local model deployment and maintenance
- OpenAI embeddings: Not specified in requirements
- Hugging Face models: More complex deployment

## 4. Knowledge Graph Extraction

**Decision**: Use spaCy with custom entity relation extraction
**Rationale**: spaCy provides excellent NLP capabilities for entity recognition. Custom relation extraction can be built on top to identify relationships between entities.
**Alternatives considered**:
- OpenIE: More complex setup
- Stanford CoreNLP: Heavy dependency
- Custom transformer models: Overkill for initial implementation

## 5. Memgraph Integration

**Decision**: Use neo4j Python driver for Memgraph connectivity
**Rationale**: Memgraph is compatible with Neo4j's Cypher query language and supports the Bolt protocol. The neo4j driver is well-maintained and documented.
**Alternatives considered**:
- Memgraph's own drivers: Less mature ecosystem
- Custom REST API wrapper: Unnecessary complexity

## 6. Query Expansion Techniques

**Decision**: Implement synonym-based expansion using WordNet
**Rationale**: WordNet provides a good balance of coverage and simplicity for query expansion. It's lightweight and doesn't require additional API calls.
**Alternatives considered**:
- Thesaurus APIs: Additional dependency and potential cost
- Embedding-based expansion: More complex implementation
- LLM-based expansion: Overkill for basic expansion

## 7. Hybrid Search Implementation

**Decision**: Combine vector similarity with keyword search using BM25
**Rationale**: BM25 is a proven algorithm for keyword search that complements vector similarity well. This approach provides robust retrieval capabilities.
**Alternatives considered**:
- Pure vector search: May miss keyword-matching results
- Pure keyword search: Doesn't capture semantic similarity
- Complex ensemble methods: Premature optimization

## 8. Result Re-ranking

**Decision**: Use DashScopeRerank API
**Rationale**: As specified in requirements, this is the designated re-ranking service. Using the API avoids local model deployment.
**Alternatives considered**:
- Cross-encoder models locally: Requires deployment and maintenance
- Simple scoring combinations: Less effective than dedicated rerankers

## 9. LLM Integration

**Decision**: Use Qwen3-Max via DashScope API
**Rationale**: As specified in requirements, this is the designated LLM. Using the API service avoids local model deployment complexity.
**Alternatives considered**:
- Local LLM deployment: Complex setup and resource requirements
- Other cloud providers: Not specified in requirements

## 10. CLI Interface Design

**Decision**: Use argparse for command-line parsing
**Rationale**: argparse is part of Python's standard library and provides robust command-line parsing capabilities. It's well-documented and widely used.
**Alternatives considered**:
- Click: Additional dependency
- Typer: Additional dependency
- Custom parsing: Unnecessary complexity

## 11. Configuration Management

**Decision**: Use python-dotenv for environment variable management
**Rationale**: python-dotenv is a lightweight library that simplifies environment variable loading from .env files. It's widely used and well-maintained.
**Alternatives considered**:
- Custom configuration parsing: Unnecessary complexity
- ConfigParser: Less flexible for environment variables