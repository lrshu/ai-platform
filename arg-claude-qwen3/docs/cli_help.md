# RAG Backend System CLI Help

This document provides comprehensive help and usage information for the RAG Backend System command-line interface.

## Overview

The RAG Backend System CLI provides three main commands:
1. `indexing` - Index PDF documents into collections
2. `search` - Search indexed documents using hybrid retrieval
3. `chat` - Have a conversation with indexed documents using LLMs

## Basic Usage

```bash
python main.py [command] [options]
```

To see available commands and global help:
```bash
python main.py --help
```

To see help for a specific command:
```bash
python main.py [command] --help
```

## Commands

### Indexing Command

Index a PDF document into a named collection.

```bash
python main.py indexing --name COLLECTION_NAME --file PATH_TO_PDF
```

**Options:**
- `--name` (required): Name of the document collection
- `--file` (required): Path to the PDF file to index

**Example:**
```bash
python main.py indexing --name my_documents --file /path/to/document.pdf
```

### Search Command

Search for relevant document chunks using hybrid retrieval.

```bash
python main.py search --name COLLECTION_NAME --question QUESTION [--top-k N] [search_options]
```

**Options:**
- `--name` (required): Name of the document collection to search
- `--question` (required): The question or search query
- `--top-k` (optional): Number of results to return (default: 5)
- `--no-expand` (optional): Disable query expansion
- `--no-rerank` (optional): Disable result re-ranking
- `--no-vector` (optional): Disable vector search
- `--no-graph` (optional): Disable graph search

**Example:**
```bash
python main.py search --name my_documents --question "What is machine learning?" --top-k 10
```

### Chat Command

Have a conversation with indexed documents using LLMs.

```bash
python main.py chat --name COLLECTION_NAME --question QUESTION [--session-id ID] [--top-k N] [search_options]
```

**Options:**
- `--name` (required): Name of the document collection to chat with
- `--question` (required): The question to ask
- `--session-id` (optional): Session identifier for maintaining context
- `--top-k` (optional): Number of results to return (default: 5)
- `--no-expand` (optional): Disable query expansion
- `--no-rerank` (optional): Disable result re-ranking
- `--no-vector` (optional): Disable vector search
- `--no-graph` (optional): Disable graph search

**Example:**
```bash
python main.py chat --name my_documents --question "Explain the concept of neural networks" --session-id session123
```

## Environment Variables

The CLI uses the following environment variables:

- `QWEN_API_KEY`: API key for Qwen models (required)
- `DATABASE_URL`: Memgraph database connection URL (default: bolt://127.0.0.1:7687)
- `DATABASE_USER`: Database username (if required)
- `DATABASE_PASSWORD`: Database password (if required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Log file path (default: console only)
- `MAX_CHUNK_SIZE`: Maximum document chunk size (default: 1000)
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent API requests (default: 10)
- `DEBUG`: Enable debug mode (default: false)

## Examples

### Indexing Documents

```bash
# Index a single document
python main.py indexing --name research_papers --file ./papers/ai_overview.pdf

# Index another document into the same collection
python main.py indexing --name research_papers --file ./papers/deep_learning.pdf
```

### Searching Documents

```bash
# Simple search
python main.py search --name research_papers --question "What are transformers in NLP?"

# Search with more results
python main.py search --name research_papers --question "Neural network architectures" --top-k 15

# Search with disabled features
python main.py search --name research_papers --question "Computer vision applications" --no-graph --no-expand
```

### Chatting with Documents

```bash
# Start a new chat session
python main.py chat --name research_papers --question "Summarize the key points about machine learning"

# Continue with context using session ID
python main.py chat --name research_papers --question "Can you elaborate on the first point?" --session-id sess_abc123
```

## Error Handling

The CLI provides detailed error messages for common issues:
- Invalid collection names
- Missing or invalid file paths
- Database connection errors
- API key validation errors
- Rate limiting errors

All errors are logged according to the configured logging level.

## Docker Usage

When running in Docker, use the same commands with the docker exec syntax:

```bash
# Index a document
docker exec -it rag-backend python main.py indexing --name my_collection --file /app/data/document.pdf

# Search documents
docker exec -it rag-backend python main.py search --name my_collection --question "What is this about?"

# Chat with documents
docker exec -it rag-backend python main.py chat --name my_collection --question "Can you explain this?"
```

Note that file paths in Docker should be relative to the container's file system.