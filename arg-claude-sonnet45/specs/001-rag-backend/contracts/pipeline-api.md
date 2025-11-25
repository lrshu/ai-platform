# Pipeline API Contract

**Version**: 1.0.0
**Date**: 2025-11-22

## Overview

Internal Python API for RAG pipeline components. Defines function signatures, inputs, outputs, and error handling for each pipeline stage.

---

## Module: `indexing.py`

### `parse_pdf(file_path: str) -> str`

**Purpose**: Parse PDF file and convert to markdown format.

**Input**:
- `file_path` (str): Absolute path to PDF file

**Output**:
- (str): Markdown-formatted text content

**Raises**:
- `FileNotFoundError`: If file_path does not exist
- `ValueError`: If file is not a valid PDF
- `RuntimeError`: If parsing fails (corrupted PDF, unsupported format)

**Example**:
```python
markdown_content = parse_pdf("/path/to/document.pdf")
```

---

### `chunk_text(markdown: str, chunk_size: int = 512, overlap: int = 50) -> list[str]`

**Purpose**: Split markdown text into semantically coherent chunks.

**Input**:
- `markdown` (str): Markdown-formatted text
- `chunk_size` (int, default=512): Target size per chunk in characters
- `overlap` (int, default=50): Character overlap between consecutive chunks

**Output**:
- (list[str]): List of text chunks

**Raises**:
- `ValueError`: If chunk_size < 100 or overlap >= chunk_size

**Example**:
```python
chunks = chunk_text(markdown_content, chunk_size=512, overlap=50)
```

---

### `embed_chunks(chunks: list[str]) -> list[tuple[str, list[float]]]`

**Purpose**: Generate embeddings for text chunks using Qwen text-embedding-v4.

**Input**:
- `chunks` (list[str]): List of text chunks

**Output**:
- (list[tuple[str, list[float]]]): List of (chunk_text, embedding_vector) pairs
  - embedding_vector is 1024-dimensional

**Raises**:
- `RuntimeError`: If embedding API is unavailable or returns error
- `ValueError`: If chunks list is empty

**Implementation Notes**:
- Batch embed up to 25 chunks per API call
- Retry with exponential backoff on rate limit errors
- Log warning if any chunk embedding fails, skip that chunk

**Example**:
```python
embedded_chunks = embed_chunks(chunks)
for text, embedding in embedded_chunks:
    assert len(embedding) == 1024
```

---

### `store_document(name: str, embeddings: list[tuple[str, list[float]]], metadata: dict) -> UUID`

**Purpose**: Store document chunks with embeddings in Chroma and metadata in Memgraph.

**Input**:
- `name` (str): Document namespace/collection name
- `embeddings` (list[tuple[str, list[float]]]): Chunk texts and embeddings
- `metadata` (dict): Document metadata
  - Required keys: `filename`, `file_path`, `file_size`

**Output**:
- (UUID): Unique document ID

**Raises**:
- `ValueError`: If name is invalid format or metadata missing required keys
- `RuntimeError`: If storage operations fail (Chroma or Memgraph errors)

**Side Effects**:
- Creates Chroma collection `docs_{name}` if not exists
- Inserts Document node and Chunk nodes in Memgraph
- Creates CONTAINS relationships

**Example**:
```python
doc_id = store_document(
    name="technical-docs",
    embeddings=embedded_chunks,
    metadata={"filename": "manual.pdf", "file_path": "/path/to/manual.pdf", "file_size": 2048000}
)
```

---

## Module: `pre_retrieval.py`

### `expand_query(question: str) -> str`

**Purpose**: Expand or clarify query using LLM to improve retrieval quality.

**Input**:
- `question` (str): Original user query

**Output**:
- (str): Expanded/rewritten query

**Raises**:
- `RuntimeError`: If LLM API is unavailable

**Implementation Notes**:
- Use Qwen3-Max with low temperature (0.1)
- Prompt template emphasizes adding synonyms and expanding abbreviations
- Fallback to original query if expansion fails

**Example**:
```python
original = "RAG architecture"
expanded = expand_query(original)
# Result: "RAG (Retrieval-Augmented Generation) architecture components and design patterns"
```

---

### `preprocess_query(question: str, enable_expansion: bool = False) -> str`

**Purpose**: Coordinate pre-retrieval processing.

**Input**:
- `question` (str): Original query
- `enable_expansion` (bool, default=False): Whether to apply query expansion

**Output**:
- (str): Processed query (expanded if enabled, otherwise original)

**Raises**:
- (None - fallback to original query on any errors)

**Example**:
```python
processed_query = preprocess_query("RAG", enable_expansion=True)
```

---

## Module: `retrieval.py`

### `get_query_embedding(question: str) -> list[float]`

**Purpose**: Generate embedding vector for user query.

**Input**:
- `question` (str): Query text

**Output**:
- (list[float]): 1024-dimensional embedding vector

**Raises**:
- `RuntimeError`: If embedding API fails

**Example**:
```python
query_embedding = get_query_embedding("How does RAG work?")
assert len(query_embedding) == 1024
```

---

### `vector_search(name: str, query_embedding: list[float], top_k: int = 20) -> list[dict]`

**Purpose**: Perform vector similarity search in Chroma.

**Input**:
- `name` (str): Document namespace to search
- `query_embedding` (list[float]): Query embedding vector
- `top_k` (int, default=20): Number of results to return

**Output**:
- (list[dict]): Retrieved chunks with structure:
  ```python
  {
      "chunk_id": UUID,
      "text": str,
      "similarity_score": float,  # 0-1
      "source": "vector",
      "metadata": dict,
  }
  ```

**Raises**:
- `ValueError`: If namespace does not exist
- `RuntimeError`: If Chroma query fails

**Example**:
```python
results = vector_search("technical-docs", query_embedding, top_k=20)
```

---

### `keyword_search(name: str, question: str, top_k: int = 20) -> list[dict]`

**Purpose**: Perform keyword/BM25-style search in Memgraph.

**Input**:
- `name` (str): Document namespace
- `question` (str): Query text
- `top_k` (int, default=20): Number of results

**Output**:
- (list[dict]): Retrieved chunks (same structure as vector_search)

**Raises**:
- `ValueError`: If namespace does not exist
- `RuntimeError`: If Memgraph query fails

**Implementation Notes**:
- Use Cypher full-text index on Chunk.text
- Score by term frequency and position

**Example**:
```python
results = keyword_search("technical-docs", "RAG architecture", top_k=20)
```

---

### `graph_search(name: str, question: str, top_k: int = 10) -> list[dict]`

**Purpose**: Perform graph traversal search via entity relationships (optional).

**Input**:
- `name` (str): Document namespace
- `question` (str): Query text
- `top_k` (int, default=10): Number of results

**Output**:
- (list[dict]): Retrieved chunks (same structure as vector_search)

**Raises**:
- `ValueError`: If namespace does not exist
- (None - returns empty list if entities not extracted)

**Implementation Notes**:
- Extract entities from question using NER or LLM
- Traverse Entity-Chunk relationships in Memgraph
- Optional for MVP (returns empty list if not implemented)

**Example**:
```python
results = graph_search("technical-docs", "LangChain", top_k=10)
```

---

### `hybrid_search(name: str, question: str, options: QueryOptions) -> RetrievalResult`

**Purpose**: Execute hybrid retrieval combining vector, keyword, and graph search.

**Input**:
- `name` (str): Document namespace
- `question` (str): Original or preprocessed query
- `options` (QueryOptions): Search configuration

**Output**:
- (RetrievalResult): Merged and deduplicated results

**Process**:
1. Run enabled search methods in parallel (vector, keyword, graph)
2. Merge results, deduplicate by chunk_id
3. Sort by similarity score (descending)
4. Return top 30-40 chunks

**Raises**:
- `ValueError`: If namespace does not exist or no search methods enabled
- (None - partial results returned if some methods fail)

**Example**:
```python
result = hybrid_search("technical-docs", "RAG architecture", options)
assert len(result.chunks) <= 40
```

---

## Module: `post_retrieval.py`

### `rerank_chunks(query: str, chunks: list[dict], top_k: int = 5) -> list[dict]`

**Purpose**: Rerank retrieved chunks using DashScope cross-encoder reranker.

**Input**:
- `query` (str): Original query text
- `chunks` (list[dict]): Retrieved chunks from hybrid search
- `top_k` (int, default=5): Number of top chunks to return

**Output**:
- (list[dict]): Top-k chunks sorted by rerank score

**Raises**:
- `RuntimeError`: If rerank API fails
- (None - returns original chunks on failure with warning)

**Implementation Notes**:
- Use `gte-rerank` model via DashScope
- Update similarity_score with rerank score
- Preserve chunk metadata

**Example**:
```python
top_chunks = rerank_chunks("RAG", retrieved_chunks, top_k=5)
assert len(top_chunks) == 5
```

---

## Module: `generation.py`

### `generate_answer(question: str, chunks: list[dict]) -> GeneratedResponse`

**Purpose**: Generate natural language answer with citations using retrieved context.

**Input**:
- `question` (str): User's original question
- `chunks` (list[dict]): Top-k reranked chunks

**Output**:
- (GeneratedResponse): Answer with citations

**Raises**:
- `RuntimeError`: If LLM API fails
- `ValueError`: If chunks list is empty

**Implementation Notes**:
- Construct prompt with system instructions, context chunks, and question
- System prompt emphasizes citation requirements and hallucination avoidance
- Parse LLM response to extract answer and citations
- Confidence score calculated based on citation coverage

**Prompt Template**:
```
System: You are a helpful assistant. Answer the question using only the provided context.
Include citations [1], [2], etc. for each claim. If information is not in the context, say so.

Context:
[1] {chunk_text_1}
[2] {chunk_text_2}
...

Question: {question}

Answer:
```

**Example**:
```python
response = generate_answer("How does RAG work?", top_chunks)
print(response.answer_text)
# "RAG combines retrieval and generation [1]. First, documents are retrieved [2]..."
print(response.citations)
# [Citation(chunk_id=..., text_excerpt="RAG combines...", filename="manual.pdf"), ...]
```

---

## Module: `orchestration.py`

### `index_document(name: str, file_path: str, options: dict = None) -> UUID`

**Purpose**: Orchestrate complete indexing pipeline.

**Input**:
- `name` (str): Document namespace
- `file_path` (str): Path to PDF file
- `options` (dict | None): Optional overrides for chunk_size, overlap

**Output**:
- (UUID): Document ID

**Pipeline**:
1. parse_pdf(file_path) → markdown
2. chunk_text(markdown) → chunks
3. embed_chunks(chunks) → embeddings
4. store_document(name, embeddings, metadata) → document_id

**Raises**:
- Any exception from pipeline stages

**Example**:
```python
doc_id = index_document("technical-docs", "/path/to/manual.pdf")
```

---

### `search_documents(name: str, question: str, options: QueryOptions) -> list[dict]`

**Purpose**: Orchestrate retrieval pipeline and return reranked chunks.

**Input**:
- `name` (str): Document namespace
- `question` (str): User query
- `options` (QueryOptions): Search configuration

**Output**:
- (list[dict]): Top-k reranked chunks

**Pipeline**:
1. preprocess_query(question, options.expand_query) → processed_query
2. hybrid_search(name, processed_query, options) → retrieval_result
3. rerank_chunks(question, retrieval_result.chunks, options.top_k) → top_chunks

**Raises**:
- Any exception from pipeline stages

**Example**:
```python
results = search_documents("technical-docs", "RAG", options)
```

---

### `chat_with_documents(name: str, question: str, options: QueryOptions) -> GeneratedResponse`

**Purpose**: Orchestrate full RAG pipeline and return generated answer.

**Input**:
- `name` (str): Document namespace
- `question` (str): User question
- `options` (QueryOptions): Pipeline configuration

**Output**:
- (GeneratedResponse): Generated answer with citations

**Pipeline**:
1. search_documents(name, question, options) → top_chunks
2. generate_answer(question, top_chunks) → response

**Raises**:
- Any exception from pipeline stages

**Example**:
```python
response = chat_with_documents("technical-docs", "How does RAG work?", options)
print(response.answer_text)
```

---

## Default Configuration (QueryOptions)

```python
default_options = QueryOptions(
    top_k=5,
    expand_query=False,  # Disabled by default to reduce latency
    enable_reranking=True,
    enable_vector_search=True,
    enable_keyword_search=True,
    enable_graph_search=False,  # Optional, disabled if entities not extracted
)
```

---

## Error Handling Strategy

**Transient Failures** (retry with backoff):
- Embedding API rate limits
- LLM API rate limits
- Rerank API rate limits

**Permanent Failures** (raise exception):
- File not found
- Invalid PDF format
- Namespace does not exist
- Missing required configuration

**Graceful Degradation** (fallback behavior):
- Query expansion failure → use original query
- Graph search failure → skip, use vector+keyword only
- Rerank failure → return unranked results with warning
- Keyword search failure → use vector search only

---

## Logging Requirements

Log at each pipeline stage:
- Stage name
- Input summary (query, document name)
- Duration (milliseconds)
- Output summary (chunk count, result count)
- Errors/warnings

Example log entry (JSON):
```json
{
  "timestamp": "2025-11-22T10:30:45.123Z",
  "stage": "hybrid_search",
  "query_id": "7f3e8400-e29b-41d4-a716-446655440003",
  "document_name": "technical-docs",
  "duration_ms": 450,
  "vector_results": 20,
  "keyword_results": 15,
  "graph_results": 0,
  "merged_results": 28
}
```
