# CLI Interface Contract

**Version**: 1.0.0
**Date**: 2025-11-22

## Overview

Command-line interface for RAG backend operations: document indexing, search, and interactive chat.

## Command Structure

```bash
python main.py <command> [arguments] [options]
```

---

## Commands

### 1. `indexing` - Index a Document

**Purpose**: Upload and index a PDF document for retrieval.

**Syntax**:
```bash
python main.py indexing --name <namespace> --file <file_path> [options]
```

**Required Arguments**:
- `--name <namespace>` (str): Document collection namespace/name
  - Format: Alphanumeric, hyphens, underscores only
  - Example: `technical-docs`, `user_manual_v2`
- `--file <file_path>` (str): Absolute or relative path to PDF file
  - Must exist and be readable
  - Must be ≤10MB

**Optional Arguments**:
- `--chunk-size <size>` (int, default=512): Target chunk size in characters
- `--chunk-overlap <overlap>` (int, default=50): Overlap between chunks
- `--json`: Output results as JSON instead of human-readable text
- `--verbose`: Enable debug logging

**Success Output** (human-readable):
```
✓ Document indexed successfully
Document ID: 550e8400-e29b-41d4-a716-446655440000
Filename: technical_manual.pdf
Chunks created: 87
Time taken: 12.3s
```

**Success Output** (JSON with `--json`):
```json
{
  "status": "success",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "technical_manual.pdf",
  "chunk_count": 87,
  "duration_seconds": 12.3
}
```

**Error Cases**:
- **File not found**: Exit code 1, message "Error: File '<file_path>' not found"
- **File too large**: Exit code 1, message "Error: File exceeds 10MB limit (actual: <size>MB)"
- **Unsupported format**: Exit code 1, message "Error: File must be a PDF (.pdf extension required)"
- **Parsing failure**: Exit code 1, message "Error: Failed to parse PDF: <reason>"
- **Embedding API error**: Exit code 1, message "Error: Embedding service unavailable. Retry later."

**Exit Codes**:
- `0`: Success
- `1`: User error (invalid arguments, file issues)
- `2`: System error (API failures, database errors)

---

### 2. `search` - Search for Relevant Chunks

**Purpose**: Perform semantic search over indexed documents and return ranked chunks.

**Syntax**:
```bash
python main.py search --name <namespace> --question <query> [options]
```

**Required Arguments**:
- `--name <namespace>` (str): Document collection namespace to search
- `--question <query>` (str): Natural language search query
  - Minimum 3 characters
  - Quote if contains spaces: `--question "How does RAG work?"`

**Optional Arguments**:
- `--top-k <k>` (int, default=5): Number of chunks to return (1-20)
- `--expand-query`: Enable query expansion (pre-retrieval)
- `--no-rerank`: Disable reranking (post-retrieval)
- `--vector-only`: Use only vector search (disable keyword/graph)
- `--json`: Output results as JSON
- `--verbose`: Enable debug logging

**Success Output** (human-readable):
```
Found 5 relevant chunks:

[1] Similarity: 0.92 | Source: technical_manual.pdf (chunk 23)
RAG combines retrieval and generation. First, relevant documents are retrieved
based on the query. Then, an LLM generates an answer using the retrieved context...

[2] Similarity: 0.88 | Source: technical_manual.pdf (chunk 45)
The retrieval phase uses vector similarity search to find the most relevant
passages from the document index...

---
Search completed in 1.2s
```

**Success Output** (JSON with `--json`):
```json
{
  "status": "success",
  "query": "How does RAG work?",
  "results": [
    {
      "rank": 1,
      "chunk_id": "7f3e8400-e29b-41d4-a716-446655440001",
      "text": "RAG combines retrieval and generation...",
      "similarity_score": 0.92,
      "source": {
        "filename": "technical_manual.pdf",
        "chunk_position": 23
      }
    },
    {
      "rank": 2,
      "chunk_id": "7f3e8400-e29b-41d4-a716-446655440002",
      "text": "The retrieval phase uses vector similarity search...",
      "similarity_score": 0.88,
      "source": {
        "filename": "technical_manual.pdf",
        "chunk_position": 45
      }
    }
  ],
  "count": 5,
  "duration_seconds": 1.2
}
```

**Error Cases**:
- **Namespace not found**: Exit code 1, message "Error: No documents found for namespace '<namespace>'"
- **Query too short**: Exit code 1, message "Error: Query must be at least 3 characters"
- **No results found**: Exit code 0 (success), message "No relevant results found for query"
- **Embedding API error**: Exit code 2, message "Error: Embedding service unavailable"
- **Rerank API error**: Exit code 2, message "Warning: Rerank failed, returning unranked results"

**Exit Codes**:
- `0`: Success (including zero results case)
- `1`: User error
- `2`: System error

---

### 3. `chat` - Interactive Chat Interface

**Purpose**: Start an interactive chat session with RAG-based question answering.

**Syntax**:
```bash
python main.py chat --name <namespace> [options]
```

**Required Arguments**:
- `--name <namespace>` (str): Document collection namespace for chat context

**Optional Arguments**:
- `--top-k <k>` (int, default=5): Number of chunks to retrieve per query
- `--expand-query`: Enable query expansion
- `--no-rerank`: Disable reranking
- `--json`: Output each response as JSON (for programmatic use)
- `--verbose`: Enable debug logging

**Interactive Behavior**:
```
RAG Chat - Namespace: technical-docs
Type 'exit', 'quit', or Ctrl+C to end session.

You: How does RAG work?
Assistant: RAG (Retrieval-Augmented Generation) combines retrieval and generation [1].
First, relevant documents are retrieved based on the query [2]. Then, an LLM generates
an answer using the retrieved context as grounding information [1].

Sources:
[1] technical_manual.pdf (chunk 23)
[2] technical_manual.pdf (chunk 45)

You: exit
Goodbye!
```

**Success Output** (JSON mode with `--json`):
```json
{
  "query": "How does RAG work?",
  "answer": "RAG combines retrieval and generation...",
  "citations": [
    {"chunk_id": "...", "filename": "technical_manual.pdf", "position": 23},
    {"chunk_id": "...", "filename": "technical_manual.pdf", "position": 45}
  ],
  "duration_seconds": 2.1
}
```

**Chat Commands**:
- `exit` or `quit`: End chat session
- `clear`: Clear conversation history (if implemented)
- `help`: Show available commands

**Error Cases**:
- **Namespace not found**: Print error and exit
- **LLM API error**: Print error, allow retry on next question
- **No results**: Print "No relevant information found in documents"

**Exit Codes**:
- `0`: Normal exit (user typed 'exit')
- `1`: Error before chat loop starts (namespace not found)
- `2`: Ctrl+C interrupt (graceful shutdown)

---

## Global Options

Available for all commands:

- `--help` or `-h`: Show help message for command
- `--version`: Show CLI version
- `--json`: Output in JSON format (machine-readable)
- `--verbose` or `-v`: Enable debug logging

---

## Environment Variables

Required before running commands (loaded from `.env` file):

```bash
# Qwen Configuration
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=sk-xxx

# Memgraph
DATABASE_URL=bolt://127.0.0.1:7687
DATABASE_USER=
DATABASE_PASSWORD=
```

---

## Exit Code Summary

| Code | Meaning | Example |
|------|---------|---------|
| 0    | Success | Command completed normally |
| 1    | User error | File not found, invalid arguments |
| 2    | System error | API failure, database unavailable |

---

## Usage Examples

### Index a document
```bash
python main.py indexing --name docs --file /path/to/manual.pdf
```

### Search with custom options
```bash
python main.py search --name docs --question "What is RAG?" --top-k 10 --expand-query
```

### Start interactive chat
```bash
python main.py chat --name docs
```

### JSON output for automation
```bash
python main.py search --name docs --question "RAG" --json | jq '.results[0].text'
```