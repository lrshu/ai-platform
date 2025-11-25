# Data Model: RAG Backend System

**Date**: 2025-11-22
**Purpose**: Define entities, relationships, and data structures for RAG backend

## Entity Definitions

### 1. Document

Represents an uploaded document in the system.

**Attributes**:
- `id` (str, UUID): Unique identifier
- `name` (str): Namespace/collection name for grouping related documents
- `filename` (str): Original filename
- `file_path` (str): Absolute path to stored PDF file
- `file_size` (int): File size in bytes
- `upload_timestamp` (datetime): When document was uploaded
- `processing_status` (enum): `pending`, `processing`, `completed`, `failed`
- `chunk_count` (int): Total number of chunks created
- `error_message` (str | None): Error details if processing failed

**Validation Rules**:
- `name` must be alphanumeric with hyphens/underscores only (collection name safe)
- `file_path` must exist and be readable
- `file_size` ≤ 10MB (configurable limit)
- `filename` must end with `.pdf`

**Storage**:
- **Memgraph**: Store document metadata as node
- **Filesystem**: Store original PDF file at `file_path`

**State Transitions**:
```
pending → processing → completed
         ↓
       failed (with error_message)
```

---

### 2. DocumentChunk

A semantically coherent segment of a document after splitting.

**Attributes**:
- `id` (str, UUID): Unique identifier
- `document_id` (str, UUID): Foreign key to parent Document
- `text` (str): Chunk text content (markdown format)
- `embedding` (list[float], 1024d): Vector embedding of text
- `position` (int): Ordinal position in document (0-indexed)
- `char_offset` (int): Character offset in original markdown
- `metadata` (dict): Additional metadata
  - `document_name` (str): Copy of parent document name
  - `filename` (str): Copy of original filename
  - `page_numbers` (list[int] | None): Source page numbers if available
  - `section_header` (str | None): Nearest markdown header

**Validation Rules**:
- `text` length ≤ 1000 characters (approx 512 tokens after chunking)
- `embedding` dimension = 1024 (Qwen embedding size)
- `position` ≥ 0 and < parent document's `chunk_count`
- `document_id` must reference existing Document

**Storage**:
- **Chroma**: Store `id`, `text`, `embedding`, `metadata` (primary storage for retrieval)
- **Memgraph**: Store `id`, `document_id`, `position` as nodes with relationships

**Relationships**:
- Belongs to one `Document` (many-to-one)
- May mention multiple `Entity` nodes (many-to-many)

---

### 3. Query

A user's search query and its processing metadata.

**Attributes**:
- `id` (str, UUID): Unique identifier
- `document_name` (str): Target document namespace to search
- `original_text` (str): User's original query
- `expanded_text` (str | None): Query after pre-retrieval expansion (if enabled)
- `timestamp` (datetime): When query was submitted
- `options` (QueryOptions): Configuration for retrieval

**QueryOptions** (nested object):
- `top_k` (int, default=5): Number of chunks to retrieve
- `expand_query` (bool, default=False): Enable query expansion
- `enable_reranking` (bool, default=True): Enable post-retrieval reranking
- `enable_vector_search` (bool, default=True): Enable vector similarity search
- `enable_keyword_search` (bool, default=True): Enable keyword/BM25 search
- `enable_graph_search` (bool, default=False): Enable graph traversal search

**Validation Rules**:
- `original_text` length ≥ 3 characters
- `document_name` must exist in system
- `top_k` ∈ [1, 20]
- At least one search method must be enabled

**Storage**:
- **Transient**: Not persisted (only in-memory during request)
- **Logging**: Query logged to structured logs for analytics

---

### 4. RetrievalResult

Output from the retrieval phase (vector + keyword + graph search).

**Attributes**:
- `query_id` (str, UUID): Reference to originating Query
- `chunks` (list[RetrievedChunk]): Ranked list of retrieved chunks
- `retrieval_methods_used` (list[str]): Which methods contributed (e.g., `["vector", "keyword"]`)
- `timestamp` (datetime): When retrieval completed
- `retrieval_duration_ms` (int): Time taken for retrieval

**RetrievedChunk** (nested object):
- `chunk_id` (str, UUID): Reference to DocumentChunk
- `text` (str): Chunk text content
- `similarity_score` (float): Relevance score (0-1, higher is better)
- `source` (str): Retrieval method that returned this chunk (`vector`, `keyword`, `graph`)
- `metadata` (dict): Chunk metadata (filename, position, etc.)

**Validation Rules**:
- `chunks` list may be empty (no results found)
- `similarity_score` ∈ [0, 1]
- `chunks` should be sorted by `similarity_score` descending

**Storage**:
- **Transient**: Not persisted (passed to generation stage)
- **Logging**: Log retrieval stats (count, duration, methods used)

---

### 5. GeneratedResponse

Final answer produced by the generation phase.

**Attributes**:
- `id` (str, UUID): Unique identifier
- `query_id` (str, UUID): Reference to originating Query
- `answer_text` (str): Generated natural language answer
- `citations` (list[Citation]): Source references
- `confidence_score` (float | None): Confidence in answer quality (0-1)
- `timestamp` (datetime): When generation completed
- `generation_duration_ms` (int): Time taken for generation

**Citation** (nested object):
- `chunk_id` (str, UUID): Referenced DocumentChunk
- `text_excerpt` (str): Quoted text from chunk (≤100 chars)
- `filename` (str): Source document filename

**Validation Rules**:
- `answer_text` length ≥ 10 characters (minimum answer)
- `citations` list should not be empty (unless insufficient context)
- Each citation must reference a chunk from RetrievalResult

**Storage**:
- **Transient**: Not persisted for MVP (return to user and log)
- **Future**: Could store in Memgraph for conversation history

---

### 6. Entity (Optional - Future Enhancement)

Named entity extracted from document chunks for graph-based retrieval.

**Attributes**:
- `name` (str): Entity name (e.g., "Python", "LangChain")
- `type` (str): Entity type (e.g., "technology", "concept", "person")
- `mention_count` (int): Number of times mentioned across all chunks

**Relationships**:
- Mentioned in multiple `DocumentChunk` nodes (many-to-many)
- Related to other `Entity` nodes (many-to-many)

**Storage**:
- **Memgraph**: Store as nodes with `:MENTIONS` and `:RELATED_TO` relationships

**Note**: Entity extraction is optional for MVP. Can be added in post-MVP iterations using NER models or LLM extraction.

---

## Relationships (Graph Schema)

### Memgraph Cypher Schema

```cypher
// Node definitions
CREATE CONSTRAINT ON (d:Document) ASSERT d.id IS UNIQUE;
CREATE CONSTRAINT ON (c:Chunk) ASSERT c.id IS UNIQUE;
CREATE INDEX ON :Document(name);
CREATE INDEX ON :Chunk(document_id);

// Relationship definitions
(:Document {id, name, filename, file_path, upload_timestamp, chunk_count, processing_status})
  -[:CONTAINS {position}]->
(:Chunk {id, document_id, position, char_offset})

// Future: Entity relationships
(:Chunk)-[:MENTIONS]->(:Entity {name, type})
(:Entity)-[:RELATED_TO {strength}]->(:Entity)
```

### Chroma Collection Schema

```python
# Collection per document namespace
collection_name = f"docs_{document_name}"

# Document schema in Chroma
{
    "ids": [chunk.id],                    # UUID as string
    "documents": [chunk.text],            # Chunk text
    "embeddings": [chunk.embedding],      # 1024d vector
    "metadatas": [{                       # Metadata dict
        "document_id": chunk.document_id,
        "document_name": document_name,
        "filename": filename,
        "position": chunk.position,
        "char_offset": chunk.char_offset,
        "section_header": section_header or "",
    }]
}
```

---

## Data Flow Diagrams

### Indexing Flow

```
PDF File → Parser (pymupdf4llm) → Markdown
  ↓
Markdown → Text Splitter → Chunks (text)
  ↓
Chunks → Embedding Model → Chunks (text + embedding)
  ↓
├─→ Chroma: Store (id, text, embedding, metadata)
└─→ Memgraph: Store Document node, Chunk nodes, CONTAINS relationships
```

### Retrieval Flow

```
User Query
  ↓
Pre-Retrieval (optional) → Expanded Query
  ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ Vector Search   │ Keyword Search  │ Graph Search    │
│ (Chroma)        │ (Memgraph)      │ (Memgraph)      │
│ → top 20 chunks │ → top 20 chunks │ → top 10 chunks │
└─────────────────┴─────────────────┴─────────────────┘
  ↓
Merge & Deduplicate → ~30-40 unique chunks
  ↓
Post-Retrieval Reranking (DashScope) → top 5 chunks
  ↓
RetrievalResult
```

### Generation Flow

```
RetrievalResult (top 5 chunks)
  ↓
Prompt Template: Query + Context Chunks + Instructions
  ↓
LLM (Qwen3-Max) → Generated Answer + Citations
  ↓
Response Parsing → Extract citations, format output
  ↓
GeneratedResponse
```

---

## Type Definitions (Python)

```python
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

# Document
class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    filename: str
    file_path: str
    file_size: int
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_status: Literal["pending", "processing", "completed", "failed"] = "pending"
    chunk_count: int = 0
    error_message: str | None = None

# DocumentChunk
class ChunkMetadata(BaseModel):
    document_name: str
    filename: str
    page_numbers: list[int] | None = None
    section_header: str | None = None

class DocumentChunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    text: str
    embedding: list[float]  # 1024 dimensions
    position: int
    char_offset: int
    metadata: ChunkMetadata

# Query
class QueryOptions(BaseModel):
    top_k: int = 5
    expand_query: bool = False
    enable_reranking: bool = True
    enable_vector_search: bool = True
    enable_keyword_search: bool = True
    enable_graph_search: bool = False

class Query(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_name: str
    original_text: str
    expanded_text: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    options: QueryOptions = Field(default_factory=QueryOptions)

# RetrievalResult
class RetrievedChunk(BaseModel):
    chunk_id: UUID
    text: str
    similarity_score: float
    source: Literal["vector", "keyword", "graph"]
    metadata: dict

class RetrievalResult(BaseModel):
    query_id: UUID
    chunks: list[RetrievedChunk]
    retrieval_methods_used: list[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retrieval_duration_ms: int

# GeneratedResponse
class Citation(BaseModel):
    chunk_id: UUID
    text_excerpt: str
    filename: str

class GeneratedResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    query_id: UUID
    answer_text: str
    citations: list[Citation]
    confidence_score: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    generation_duration_ms: int
```

---

## Storage Size Estimates

**Per Document** (assuming 100 pages, ~500 words/page):
- Original PDF: ~2-5 MB
- Markdown text: ~250 KB
- Chunks (text only): ~250 KB
- Embeddings (1024d × 100 chunks × 4 bytes): ~400 KB
- Memgraph nodes/relationships: ~50 KB

**Total per document**: ~3-6 MB

**For 1,000 documents**:
- Storage: ~3-6 GB
- Chroma index: ~400 MB (embeddings)
- Memgraph database: ~50 MB (metadata only)

All values within acceptable limits for MVP deployment.
