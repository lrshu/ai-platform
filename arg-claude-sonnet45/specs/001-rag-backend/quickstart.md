# Quickstart Guide: RAG Backend System

**Version**: 1.0.0
**Date**: 2025-11-22

## Prerequisites

- Python 3.12+ installed
- uv package manager installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Memgraph database running locally or remotely
- Qwen API key from DashScope

---

## Setup

### 1. Clone Repository and Navigate

```bash
cd arg-claude-v5
```

### 2. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

**Required Dependencies** (will be in `pyproject.toml`):
```toml
[project]
dependencies = [
    "langchain>=0.3.0",
    "langchain-community>=0.3.0",
    "langchain-openai>=0.2.0",
    "langchain-chroma>=0.1.0",
    "chromadb>=0.5.0",
    "pymupdf4llm>=0.1.0",
    "neo4j>=5.20.0",
    "openai>=1.40.0",
    "dashscope>=1.20.0",
    "pydantic>=2.8.0",
    "pydantic-settings>=2.4.0",
]
```

### 3. Start Memgraph

**Option A: Docker** (recommended)
```bash
docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform
```

**Option B: Native Installation**
- Download from https://memgraph.com/download
- Follow installation instructions for your OS

Verify Memgraph is running:
```bash
# Should connect successfully
echo "RETURN 1;" | docker exec -i memgraph mgconsole
```

### 4. Configure Environment

Create `.env` file in project root:

```bash
# QWen Configuration
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=sk-bac503b5a123456aa106e9574c89b0a0

# Memgraph
DATABASE_URL=bolt://127.0.0.1:7687
DATABASE_USER=
DATABASE_PASSWORD=

# Optional: RAG Configuration
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
```

**Security Note**: Never commit `.env` to git. Add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

---

## Quick Test

### 1. Index a Sample Document

Download a sample PDF or use your own:

```bash
python src/cli/main.py indexing \
  --name test-docs \
  --file /path/to/sample.pdf
```

Expected output:
```
✓ Document indexed successfully
Document ID: 550e8400-e29b-41d4-a716-446655440000
Filename: sample.pdf
Chunks created: 25
Time taken: 5.2s
```

### 2. Search Documents

```bash
python src/cli/main.py search \
  --name test-docs \
  --question "What is the main topic of the document?"
```

Expected output:
```
Found 5 relevant chunks:

[1] Similarity: 0.94 | Source: sample.pdf (chunk 3)
This document discusses the fundamentals of machine learning...

[2] Similarity: 0.89 | Source: sample.pdf (chunk 7)
Machine learning algorithms can be categorized into supervised...
```

### 3. Interactive Chat

```bash
python src/cli/main.py chat --name test-docs
```

Expected interaction:
```
RAG Chat - Namespace: test-docs
Type 'exit', 'quit', or Ctrl+C to end session.

You: What are the key concepts?
Assistant: The key concepts include [1] machine learning fundamentals...

Sources:
[1] sample.pdf (chunk 3)

You: exit
Goodbye!
```

---

## Common Operations

### Index Multiple Documents

```bash
# Index documents with different names (namespaces)
python src/cli/main.py indexing --name research --file research_paper.pdf
python src/cli/main.py indexing --name manuals --file user_manual.pdf
python src/cli/main.py indexing --name reference --file reference_guide.pdf
```

### Search with Options

```bash
# More results
python src/cli/main.py search --name research --question "RAG" --top-k 10

# Enable query expansion
python src/cli/main.py search --name research --question "ML" --expand-query

# JSON output for scripting
python src/cli/main.py search --name research --question "RAG" --json
```

### Debug Mode

```bash
# Enable verbose logging
python src/cli/main.py indexing --name test --file doc.pdf --verbose
```

---

## Verify Installation

Create a test script `test_setup.py`:

```python
#!/usr/bin/env python
"""Verify RAG backend setup."""

import os
from dotenv import load_dotenv
import chromadb
from neo4j import GraphDatabase

def test_env_vars():
    """Check environment variables."""
    load_dotenv()
    required = ["QWEN_API_KEY", "QWEN_API_BASE", "DATABASE_URL"]
    for var in required:
        if not os.getenv(var):
            print(f"❌ Missing {var}")
            return False
    print("✓ Environment variables configured")
    return True

def test_chroma():
    """Test Chroma connection."""
    try:
        client = chromadb.Client()
        print("✓ Chroma working")
        return True
    except Exception as e:
        print(f"❌ Chroma error: {e}")
        return False

def test_memgraph():
    """Test Memgraph connection."""
    try:
        load_dotenv()
        driver = GraphDatabase.driver(os.getenv("DATABASE_URL"))
        with driver.session() as session:
            result = session.run("RETURN 1 AS num")
            assert result.single()["num"] == 1
        driver.close()
        print("✓ Memgraph connection successful")
        return True
    except Exception as e:
        print(f"❌ Memgraph error: {e}")
        return False

def test_qwen_api():
    """Test Qwen API key."""
    try:
        from dashscope import TextEmbedding
        load_dotenv()
        response = TextEmbedding.call(
            model="text-embedding-v4",
            input=["test"],
            api_key=os.getenv("QWEN_API_KEY")
        )
        if response.status_code == 200:
            print("✓ Qwen API key valid")
            return True
        else:
            print(f"❌ Qwen API error: {response.message}")
            return False
    except Exception as e:
        print(f"❌ Qwen API error: {e}")
        return False

if __name__ == "__main__":
    print("Testing RAG Backend Setup\n" + "=" * 40)
    all_pass = all([
        test_env_vars(),
        test_chroma(),
        test_memgraph(),
        test_qwen_api(),
    ])
    print("=" * 40)
    if all_pass:
        print("\n✓ All checks passed! Ready to go.")
    else:
        print("\n❌ Some checks failed. Fix issues above.")
```

Run verification:
```bash
python test_setup.py
```

Expected output:
```
Testing RAG Backend Setup
========================================
✓ Environment variables configured
✓ Chroma working
✓ Memgraph connection successful
✓ Qwen API key valid
========================================

✓ All checks passed! Ready to go.
```

---

## Troubleshooting

### Issue: `FileNotFoundError: .env file not found`

**Solution**: Create `.env` file in project root with required variables.

```bash
cp .env.example .env  # If example exists
# OR
cat > .env << EOF
QWEN_API_KEY=your-key-here
DATABASE_URL=bolt://127.0.0.1:7687
EOF
```

---

### Issue: `Connection refused` to Memgraph

**Check if Memgraph is running**:
```bash
docker ps | grep memgraph
```

**Start Memgraph if not running**:
```bash
docker run -d -p 7687:7687 --name memgraph memgraph/memgraph-platform
```

**Check connection**:
```bash
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://127.0.0.1:7687'); driver.verify_connectivity(); print('OK')"
```

---

### Issue: `Invalid API key` for Qwen

**Verify API key format**:
- Should start with `sk-`
- Get key from https://dashscope.console.aliyun.com/

**Test manually**:
```bash
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings \
  -H "Authorization: Bearer sk-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-v4","input":"test"}'
```

---

### Issue: `ModuleNotFoundError: No module named 'langchain'`

**Reinstall dependencies**:
```bash
uv sync --reinstall
# OR
pip install --force-reinstall -r requirements.txt
```

---

### Issue: PDF parsing fails

**Check PDF format**:
- Must be a text-based PDF (not scanned image)
- File size must be ≤10MB
- File must be readable

**Test PDF parsing**:
```python
import pymupdf4llm
text = pymupdf4llm.to_markdown("yourfile.pdf")
print(text[:500])  # Should show markdown text
```

---

### Issue: Slow indexing

**Expected performance**: ~10 pages/second

**If slower, check**:
- Network latency to Qwen API
- Memgraph write performance (check Docker resources)
- PDF file complexity (tables, images slow parsing)

**Optimize**:
- Use faster machine
- Increase chunk size (fewer API calls)
- Batch embed multiple chunks per API call

---

### Issue: No search results

**Debug steps**:
1. Verify document indexed: Check Chroma collection exists
2. Check query embedding: Enable `--verbose` to see embedding values
3. Verify similarity threshold: Try lowering threshold or increasing `--top-k`

**Manual check**:
```python
import chromadb
client = chromadb.Client()
collection = client.get_collection("docs_test-docs")
print(f"Chunks indexed: {collection.count()}")
```

---

## Next Steps

1. **Read Architecture Docs**: See `specs/001-rag-backend/data-model.md` for entity details
2. **Review Contracts**: See `specs/001-rag-backend/contracts/` for API specs
3. **Run Tests**: Execute test suite (once implemented) with `pytest`
4. **Implement Tasks**: Follow `specs/001-rag-backend/tasks.md` (generated by `/speckit.tasks`)

---

## Useful Commands

```bash
# Check Python version
python --version  # Should be 3.12+

# Check uv version
uv --version

# List installed packages
uv pip list

# View Memgraph schema
docker exec -it memgraph mgconsole -e "SHOW NODE LABELS;"

# View Chroma collections
python -c "import chromadb; print(chromadb.Client().list_collections())"

# View logs with timestamps
python src/cli/main.py search --name docs --question "test" --verbose 2>&1 | grep -E "(timestamp|duration)"
```

---

## Resources

- **LangChain Docs**: https://python.langchain.com/docs/
- **Memgraph Docs**: https://memgraph.com/docs
- **Chroma Docs**: https://docs.trychroma.com/
- **Qwen API Docs**: https://help.aliyun.com/zh/dashscope/
- **Project Spec**: `specs/001-rag-backend/spec.md`

---

**Questions or Issues?**

Check the troubleshooting section above or refer to project documentation in `specs/001-rag-backend/`.
