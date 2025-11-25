# Research: RAG Backend System Technology Decisions

**Date**: 2025-11-22
**Purpose**: Resolve technical unknowns and document technology choices for RAG backend implementation

## 1. Vector Database Selection

**Decision**: **Chroma** (embedded mode for MVP)

**Rationale**:
- **Simplicity**: Embedded mode requires no separate server process - perfect for MVP
- **LangChain Integration**: First-class support in LangChain with extensive documentation
- **Python-Native**: Pure Python implementation, easy debugging and deployment
- **Feature-Complete**: Supports metadata filtering, multiple distance metrics, persistence
- **Migration Path**: Can upgrade to client-server mode for production scaling
- **Local Development**: Works seamlessly with uv/pip, no Docker required for development

**Alternatives Considered**:
- **FAISS**: Excellent performance but no built-in metadata storage, requires separate indexing strategy
- **Qdrant**: Powerful but requires separate server deployment, overkill for MVP
- **Milvus**: Enterprise-grade but complex setup, heavy resource footprint
- **Weaviate**: Feature-rich but requires separate service, adds deployment complexity

**Implementation Notes**:
- Use `langchain-chroma` package
- Store index in `./data/chroma` directory
- Configure collection per document namespace (allows multi-tenant future expansion)
- Enable persistence for durability across restarts

---

## 2. PDF to Markdown Parsing

**Decision**: **pymupdf4llm** (MuPDF-based)

**Rationale**:
- **Markdown Output**: Directly outputs markdown format preserving structure (headers, lists, tables)
- **Quality**: Better layout analysis than pypdf, tesseract, or pdfminer
- **LLM-Optimized**: Designed specifically for LLM ingestion pipelines
- **Speed**: C-based MuPDF backend is fast (~10 pages/second achievable)
- **Table Handling**: Preserves table structure as markdown tables
- **No OCR Required**: Works with text-based PDFs (OCR fallback can be added later if needed)

**Alternatives Considered**:
- **pypdf/PyPDF2**: Basic text extraction, loses formatting and structure
- **pdfplumber**: Good for tables but complex API, slower
- **unstructured.io**: Comprehensive but heavy dependencies, overkill for MVP
- **LlamaIndex loaders**: Wrapper around other libraries, adds unnecessary abstraction layer

**Implementation Notes**:
- Use `pymupdf4llm.to_markdown(file_path)` for conversion
- Chunk the resulting markdown (not the PDF pages) for better semantic coherence
- Store original PDF path in metadata for reference

---

## 3. Text Chunking Strategy

**Decision**: **Recursive Character Splitter** with markdown-aware splitting

**Rationale**:
- **Semantic Coherence**: Respects markdown structure (splits on headers, paragraphs before arbitrary char limits)
- **Configurability**: Supports overlap (50 tokens default) to prevent context loss at boundaries
- **LangChain Native**: `RecursiveCharacterTextSplitter` is battle-tested and well-documented
- **Size Control**: Target 512 tokens per chunk fits embedding model context and balances granularity
- **Header Hierarchy**: Preserves document structure metadata (section headers) in chunk metadata

**Alternatives Considered**:
- **Fixed-size splitting**: Simple but breaks sentences/paragraphs arbitrarily
- **Sentence-based splitting**: More semantic but variable chunk sizes complicate vector search
- **Token-based splitting**: Requires tokenizer dependency, adds complexity
- **Semantic chunking**: ML-based approaches are slower and require additional models

**Implementation Notes**:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,  # tokens (approximate via char count)
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len,  # character-based, convert to token estimate
)
```

---

## 4. Embedding Model Configuration

**Decision**: **Qwen text-embedding-v4** via DashScope API

**Rationale**:
- **Specified in Requirements**: User-provided tech stack specifies Qwen embedding
- **Quality**: State-of-the-art Chinese+English multilingual embedding model
- **Dimension**: 1024d embeddings balance quality and storage efficiency
- **API-Based**: No local model hosting required, reduces infrastructure complexity
- **Compatibility**: Works via DashScope SDK with LangChain integration

**Implementation Notes**:
```python
from dashscope import TextEmbedding

def get_embeddings(texts: list[str]) -> list[list[float]]:
    response = TextEmbedding.call(
        model="text-embedding-v4",
        input=texts,
        api_key=os.getenv("QWEN_API_KEY")
    )
    return [item["embedding"] for item in response.output["embeddings"]]
```

**Rate Limits & Retry**:
- Implement exponential backoff for rate limit errors
- Batch embed up to 25 chunks per API call (DashScope batch limit)
- Cache embeddings in Chroma to avoid re-embedding same content

---

## 5. Graph Storage Schema (Memgraph)

**Decision**: **Document-Chunk-Entity** graph model

**Rationale**:
- **Relationships**: Capture document → chunks, chunks → entities, entities → related entities
- **Query Patterns**: Enable graph-based retrieval (e.g., "find chunks mentioning entities related to X")
- **Metadata**: Store document metadata in graph for unified querying
- **Cypher Queries**: Use Neo4j Cypher query language (supported by Memgraph)

**Schema Design**:
```cypher
// Nodes
(:Document {id, name, file_path, upload_timestamp, chunk_count})
(:Chunk {id, document_id, text, position, char_offset})
(:Entity {name, type})  // Extracted entities (optional for MVP)

// Relationships
(:Document)-[:CONTAINS]->(:Chunk)
(:Chunk)-[:MENTIONS]->(:Entity)
(:Entity)-[:RELATED_TO]->(:Entity)
```

**Implementation Notes**:
- Use `neo4j` Python driver with Memgraph connection string
- Index `Document.name` and `Chunk.id` for fast lookup
- Store chunk embeddings in Chroma, reference by `chunk.id` in both systems
- Graph retrieval: Use Cypher to find related chunks via entity relationships

---

## 6. LLM Integration (Qwen3-Max)

**Decision**: **OpenAI-compatible API** via Qwen DashScope

**Rationale**:
- **Specified in Requirements**: User-provided tech stack specifies Qwen3-Max
- **OpenAI Compatibility**: DashScope provides OpenAI-compatible endpoint, use `openai` library
- **LangChain Integration**: `ChatOpenAI` class works with custom base URL
- **Streaming Support**: Enables progressive response display for chat interface

**Implementation Notes**:
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-max",
    openai_api_base=os.getenv("QWEN_API_BASE"),
    openai_api_key=os.getenv("QWEN_API_KEY"),
    temperature=0.1,  # Low temperature for factual RAG responses
    max_tokens=2000,
)
```

**Prompt Engineering**:
- System prompt: Emphasize citation requirements and hallucination avoidance
- User prompt template: Include retrieved chunks with source IDs for citation
- Output parsing: Extract citations from generated answer

---

## 7. Reranking Strategy

**Decision**: **DashScopeRerank** API

**Rationale**:
- **Specified in Requirements**: User-provided tech stack specifies DashScopeRerank
- **Cross-Encoder**: More accurate relevance scoring than embedding similarity alone
- **Hybrid Search Enhancement**: Reorders combined results from vector+keyword+graph searches
- **API-Based**: No model hosting required

**Implementation Notes**:
```python
from dashscope import Rerank

def rerank_chunks(query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
    response = Rerank.call(
        model="gte-rerank",
        query=query,
        documents=[chunk["text"] for chunk in chunks],
        top_n=top_k,
        api_key=os.getenv("QWEN_API_KEY")
    )
    # Return top_k chunks sorted by rerank score
    ranked_indices = [item["index"] for item in response.output["results"]]
    return [chunks[i] for i in ranked_indices[:top_k]]
```

---

## 8. Hybrid Search Implementation

**Decision**: **Fusion Search** (weighted combination of vector, keyword, graph)

**Rationale**:
- **Vector Search**: Semantic similarity (primary signal)
- **Keyword Search**: Exact term matching (BM25-like fallback)
- **Graph Search**: Entity relationship traversal (contextual expansion)
- **Fusion**: Combine scores via Reciprocal Rank Fusion (RRF) or weighted sum

**Algorithm**:
1. **Vector Search**: Query Chroma with query embedding → top 20 chunks
2. **Keyword Search**: Full-text search on chunk text in Memgraph → top 20 chunks
3. **Graph Search**: Find chunks via entity relationships in Memgraph → top 10 chunks
4. **Merge**: De-duplicate and combine (union of results, ~30-40 unique chunks)
5. **Rerank**: Use DashScopeRerank to select top 5 most relevant

**Implementation Notes**:
- Weight vector:keyword:graph = 0.6:0.3:0.1 (tune empirically)
- Use RRF formula: `score = sum(1 / (k + rank_i))` for each retrieval method
- Fallback: If graph search returns no results, skip gracefully

---

## 9. Query Expansion Strategy

**Decision**: **LLM-based query rewriting** for ambiguous queries

**Rationale**:
- **Simplicity**: Use Qwen3-Max to expand/clarify vague queries
- **Context-Aware**: LLM understands domain context better than rule-based expansion
- **Configurable**: Can enable/disable via CLI flag (`--expand-query`)

**Implementation**:
```python
def expand_query(query: str) -> str:
    prompt = f"""Rewrite this query to be more specific and search-friendly.
    Add relevant synonyms and expand abbreviations. Keep it concise.

    Original query: {query}
    Rewritten query:"""

    response = llm.invoke(prompt)
    return response.content
```

**When to Use**:
- Only for queries <5 words (short/vague queries benefit most)
- Skip for queries with technical terms or proper nouns
- Optional feature (default OFF for MVP to reduce latency)

---

## 10. CLI Framework

**Decision**: **argparse** (Python standard library)

**Rationale**:
- **Zero Dependencies**: Included in Python standard library
- **Sufficient Features**: Supports subcommands, arguments, help text
- **Familiar**: Standard Python CLI pattern, widely documented
- **Simplicity**: No need for Click, Typer, or Fire for MVP

**Command Structure**:
```bash
python main.py indexing --name <namespace> --file <path>
python main.py search --name <namespace> --question <query> [--top-k N] [--expand-query]
python main.py chat --name <namespace>  # Interactive REPL
```

**Implementation Notes**:
- Use subparsers for commands (indexing, search, chat)
- JSON output flag: `--json` for programmatic use
- Verbose flag: `--verbose` for debug logging

---

## 11. Configuration Management

**Decision**: **pydantic-settings** with `.env` file

**Rationale**:
- **Type Safety**: Pydantic validates environment variables with type hints
- **Default Values**: Specify defaults inline with validation
- **IDE Support**: Type hints enable autocomplete
- **Validation**: Catch missing/invalid env vars at startup

**Implementation**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Qwen Configuration
    qwen_api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_api_key: str

    # Memgraph
    database_url: str = "bolt://127.0.0.1:7687"
    database_user: str = ""
    database_password: str = ""

    # RAG Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 12. Logging & Observability

**Decision**: **Python logging** with structured JSON output

**Rationale**:
- **Standard Library**: No additional dependencies
- **Structured**: JSON format for log aggregation
- **Pipeline Stages**: Log entry/exit for each RAG stage with timing
- **Error Context**: Include query ID, document ID in all logs for tracing

**Implementation**:
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "stage": record.getMessage(),
            "duration_ms": getattr(record, "duration_ms", None),
        }
        return json.dumps(log_obj)

logger = logging.getLogger("rag")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

---

## Summary of Decisions

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Vector DB | Chroma (embedded) | Simple, LangChain-native, no server required |
| Graph DB | Memgraph | User-specified, Neo4j-compatible |
| PDF Parsing | pymupdf4llm | Markdown output, fast, LLM-optimized |
| Chunking | RecursiveCharacterTextSplitter | Semantic, configurable, markdown-aware |
| Embedding | Qwen text-embedding-v4 | User-specified, high-quality |
| LLM | Qwen3-Max | User-specified, OpenAI-compatible |
| Reranking | DashScopeRerank | User-specified, cross-encoder |
| CLI | argparse | Standard library, sufficient features |
| Config | pydantic-settings | Type-safe, validated |
| Logging | JSON structured logs | Observability, debugging |

All major technical decisions resolved. Ready for Phase 1 (data model and contracts).
