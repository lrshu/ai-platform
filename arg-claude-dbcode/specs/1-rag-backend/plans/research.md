# Research & Design Decisions for RAG Backend System

## Decision: PDF Parsing to Markdown

### What was chosen: langchain_community.document_loaders.PyPDFLoader with PyPDF2 backend

### Rationale:
- PyPDFLoader is a proven component in the LangChain ecosystem
- It provides reliable PDF text extraction
- It integrates well with other LangChain components for document splitting

### Alternatives considered:
- PyMuPDF: Faster but with more complex licensing
- pdfminer.six: Very flexible but slower for large files

## Decision: Document Splitting Strategy

### What was chosen: langchain_text_splitters.RecursiveCharacterTextSplitter

### Rationale:
- Recursively splits on different separators (newlines, periods, commas)
- Preserves semantic meaning better than simple character splitting
- Creates more coherent text chunks

### Alternatives considered:
- CharacterTextSplitter: Simple but may split in the middle of sentences
- TokenTextSplitter: Splits based on token count but loses semantic boundaries

## Decision: Embedding Generation

### What was chosen: langchain_community.embeddings.QwenEmbeddings

### Rationale:
- Directly supports Qwen text-embedding-v4
- Integrates seamlessly with LangChain vector stores
- Maintains consistency with the chosen LLM (Qwen3-Max)

### Alternatives considered:
- DashScopeEmbeddings: Another option for Qwen embeddings
- Other open-source embeddings: Would require additional configuration

## Decision: Knowledge Graph Extraction

### What was chosen: langchain_community.graphs.Neo4jGraph for Memgraph integration

### Rationale:
- Memgraph is compatible with Neo4j's Bolt protocol
- LangChain has built-in Neo4jGraph support
- Uses Cypher query language which is well-documented

### Alternatives considered:
- Custom Memgraph driver: Would require more implementation work
- Other graph databases: Would require changing the technology stack

## Decision: Vector Search

### What was chosen: Memgraph's vector similarity search

### Rationale:
- Native vector support in Memgraph 2.14+
- Allows combining vector search with graph queries in a single database
- Reduces architectural complexity by using one database instead of two

### Alternatives considered:
- Separate vector database (Pinecone, Weaviate): Would require additional infrastructure
- Elasticsearch with vector plugin: More complex setup

## Decision: Reranking

### What was chosen: langchain_community.rerankers.DashScopeRerank

### Rationale:
- Explicitly supports DashScopeRerank as requested in requirements
- Maintains consistency with the Alibaba Cloud ecosystem (Qwen models)

### Alternatives considered:
- BAAI/bge-reranker: Open-source alternative
- Cross-encoder models: More computationally expensive

## Decision: LLM Generation

### What was chosen: langchain_community.llms.Qwen3

### Rationale:
- Directly supports Qwen3-Max as requested in requirements
- Integrates well with other LangChain components
- Has configurable parameters for generation quality and speed

### Alternatives considered:
- DashScopeChatModel: Another option for Qwen models
- Other LLMs: Would require changing the technology stack

## Decision: Configuration Management

### What was chosen: python-dotenv library

### Rationale:
- Industry-standard for loading environment variables from .env files
- Simple to use and well-documented
- Compatible with all Python versions

### Alternatives considered:
- Manual config files: More complex to maintain
- Environment variables directly: Less user-friendly for setup

## Decision: CLI Implementation

### What was chosen: argparse library

### Rationale:
- Built-in to Python, no additional dependencies
- Simple to set up and use
- Provides good error messages and help text

### Alternatives considered:
- Click: More feature-rich but requires additional dependency
- Typer: Python 3.6+ only, but has better type hint support