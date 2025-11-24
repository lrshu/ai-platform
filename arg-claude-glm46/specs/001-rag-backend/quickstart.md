# Quickstart Guide: RAG Backend System

## Prerequisites

1. Python 3.12+
2. uv package manager
3. Memgraph database running locally
4. DashScope API key for Qwen services

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   source .venv/bin/activate
   ```

3. Set up environment variables by creating a `.env` file:
   ```env
   # QWen Configuration
   QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_API_KEY="your-api-key-here"

   # Memgraph
   DATABASE_URL="bolt://127.0.0.1:7687"
   DATABASE_USER=""
   DATABASE_PASSWORD=""
   ```

4. Start Memgraph database (if not already running)

## Usage

### 1. Index a Document

To add a PDF document to the RAG system:

```bash
python main.py indexing --name my_document --file /path/to/document.pdf
```

This command will:
- Parse the PDF document
- Extract content in markdown format
- Split content into chunks
- Generate vector embeddings for each chunk
- Extract entity relationships and build knowledge graph
- Store all data in Memgraph with the name identifier

### 2. Search for Information

To search for relevant information within indexed documents:

```bash
python main.py search --name my_document --question "What is the main topic of this document?"
```

This command will:
- Expand the query if enabled
- Perform hybrid search (vector + graph-based)
- Re-rank results if enabled
- Return the most relevant content chunks

### 3. Conversational QA

To have a conversation with the system using indexed documents as context:

```bash
python main.py chat --name my_document
```

This command will:
- Start an interactive conversation session
- Maintain context across multiple turns
- Generate answers based on retrieved document content
- Continue until the user exits

## Configuration

The system can be configured using the following environment variables:

- `QWEN_API_BASE`: Base URL for Qwen API (default: DashScope)
- `QWEN_API_KEY`: API key for Qwen services
- `DATABASE_URL`: Connection URL for Memgraph database
- `DATABASE_USER`: Username for database (if required)
- `DATABASE_PASSWORD`: Password for database (if required)

## Testing

Run the integration tests to verify the system is working correctly:

```bash
python -m pytest tests/integration/
```

## Performance Benchmarks

Expected performance characteristics:
- Indexing: 10-page PDF document in under 30 seconds
- Search: Response time under 2 seconds for 95% of queries
- Database queries: Completion within 50ms for 95% of queries