# CLI Integration Testing Guide

This guide explains how to test the CLI after refactoring to use Memgraph-only storage.

## Prerequisites

1. **Install Dependencies**
   ```bash
   # Using uv (recommended)
   uv sync --extra dev

   # Or using pip
   pip install -e ".[dev]"
   ```

2. **Start Memgraph**
   ```bash
   docker run -d -p 7687:7687 -p 7444:7444 --name memgraph memgraph/memgraph-platform

   # Verify it's running
   docker ps | grep memgraph
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your QWEN_API_KEY
   ```

## Manual Testing

### Test 1: Help Commands

Test that all help commands work:

```bash
# Main help
python -m src.cli.main --help

# Indexing help
python -m src.cli.main indexing --help

# Search help
python -m src.cli.main search --help

# Chat help
python -m src.cli.main chat --help
```

**Expected**: All commands should display help text with options.

### Test 2: Argument Validation

Test that invalid arguments are rejected:

```bash
# Missing required arguments
python -m src.cli.main indexing

# Nonexistent file
python -m src.cli.main indexing --name test --file /nonexistent.pdf

# Non-PDF file
python -m src.cli.main indexing --name test --file README.md
```

**Expected**: Each should fail with appropriate error messages.

### Test 3: Indexing (requires PDF and API key)

Create or use a test PDF, then index it:

```bash
# Index a document
python -m src.cli.main indexing \
  --name test-docs \
  --file path/to/test.pdf \
  --json

# With custom chunking
python -m src.cli.main indexing \
  --name test-docs-2 \
  --file path/to/test.pdf \
  --chunk-size 256 \
  --chunk-overlap 25 \
  --json
```

**Expected**: JSON output with `status: "success"`, document_id, and duration.

**Verify in Memgraph**:
```cypher
MATCH (d:Document) RETURN d LIMIT 5;
MATCH (c:Chunk) RETURN c LIMIT 5;
MATCH (c:Chunk) WHERE c.namespace = "test-docs" RETURN count(c);
```

### Test 4: Search

Search the indexed documents:

```bash
# Basic search
python -m src.cli.main search \
  --name test-docs \
  --question "What is the main topic?" \
  --json

# With options
python -m src.cli.main search \
  --name test-docs \
  --question "Explain the key concepts" \
  --top-k 10 \
  --expand-query \
  --json

# Vector-only search
python -m src.cli.main search \
  --name test-docs \
  --question "test query" \
  --vector-only \
  --json
```

**Expected**: JSON output with status, results array, and count.

### Test 5: Chat

Interactive chat session:

```bash
python -m src.cli.main chat --name test-docs
```

Then type questions and verify responses. Type `exit` to quit.

**Expected**:
- Greeting message
- Responses with citations
- Clean exit on "exit" command

### Test 6: Full Pipeline

Test the complete workflow:

```bash
# 1. Index
python -m src.cli.main indexing --name e2e-test --file test.pdf --json

# 2. Search
python -m src.cli.main search --name e2e-test --question "test" --json

# 3. Chat (type "exit" to quit)
python -m src.cli.main chat --name e2e-test
```

## Automated Testing

Run the test suite:

```bash
# Run all integration tests
./tests/run_integration_tests.sh

# Or manually with pytest
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_cli_basic.py -v

# Run with verbose output
pytest tests/integration/ -v --tb=short
```

## Verification Checklist

After refactoring to Memgraph-only:

- [ ] No imports of `vector_store` or `VectorStore` in codebase
- [ ] No imports of `chromadb` in codebase
- [ ] `pyproject.toml` has no Chroma dependencies
- [ ] `.env.example` has no Chroma configuration
- [ ] `src/storage/vector_store.py` deleted
- [ ] All vector operations use `GraphStore.vector_similarity_search()`
- [ ] Indexing stores both text and embeddings in Memgraph
- [ ] Keyword search retrieves full chunk data from Memgraph
- [ ] Help commands work
- [ ] Argument validation works
- [ ] Indexing creates Document and Chunk nodes with embeddings
- [ ] Vector search returns results with similarity scores
- [ ] Keyword search returns matching chunks
- [ ] Chat generates answers with citations

## Debugging

If tests fail:

1. **Check Memgraph connection**:
   ```bash
   docker logs memgraph
   nc -zv 127.0.0.1 7687
   ```

2. **Verify environment variables**:
   ```bash
   cat .env | grep -v "#"
   ```

3. **Check Python imports**:
   ```bash
   python -c "from src.storage.graph_store import GraphStore; print('✓ GraphStore imports OK')"
   python -c "from src.config.settings import settings; print('✓ Settings imports OK')"
   ```

4. **Test Memgraph directly**:
   ```bash
   docker exec -it memgraph mgconsole -e "RETURN 1;"
   ```

5. **Enable verbose logging**:
   ```bash
   python -m src.cli.main --verbose search --name test --question "test"
   ```

## Common Issues

### ModuleNotFoundError: No module named 'pydantic_settings'
**Solution**: Install dependencies with `uv sync` or `pip install -e .`

### Connection refused to Memgraph
**Solution**: Start Memgraph with `docker run -d -p 7687:7687 memgraph/memgraph-platform`

### QWEN_API_KEY not found
**Solution**: Copy `.env.example` to `.env` and add your API key

### Embedding API fails
**Solution**: Verify API key is correct and has credits at https://dashscope.console.aliyun.com/

## Test Coverage

The test suite covers:

- **CLI Interface**: Help commands, argument parsing, error handling
- **Indexing Pipeline**: PDF validation, chunking, embedding, storage in Memgraph
- **Retrieval Pipeline**: Vector search, keyword search, hybrid search
- **Generation Pipeline**: Answer generation with citations
- **End-to-End**: Complete workflow from indexing to chat

All tests use Memgraph as the unified storage backend.
