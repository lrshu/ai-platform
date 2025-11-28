# CLI Interface Contracts: RAG Backend System

## Command: indexing

Indexes a PDF document into the RAG system.

**Usage**:
```
python main.py indexing --name [name1] --file [file_path]
```

**Parameters**:
- `--name`: Required string - Name for the document collection
- `--file`: Required string - Path to the PDF file to index

**Response**:
- Success: Document ID and indexing confirmation
- Error: Descriptive error message

**Validation**:
- File must exist and be readable
- File must be a valid PDF
- Name must be unique or overwrite must be specified

## Command: search

Searches for information in indexed documents.

**Usage**:
```
python main.py search --name [name1] --question [question]
```

**Parameters**:
- `--name`: Required string - Name of the document collection to search
- `--question`: Required string - Question to ask about the documents

**Response**:
- Success: List of relevant document chunks with scores
- Error: Descriptive error message

**Validation**:
- Name must correspond to an existing document collection
- Question must not be empty

## Command: chat

Engages in a conversation about indexed documents.

**Usage**:
```
python main.py chat --name [name1]
```

**Parameters**:
- `--name`: Required string - Name of the document collection to chat about

**Interaction**:
- Prompts user for questions in a loop
- Generates answers based on document content
- Maintains conversation context

**Response**:
- Success: Generated answers to user questions
- Error: Descriptive error message

**Validation**:
- Name must correspond to an existing document collection

## Global Options

**Options available for all commands**:
- `--top_k`: Integer - Number of results to return (default: 5)
- `--expand-query`: Boolean - Enable query expansion (default: True)
- `--rerank`: Boolean - Enable result reranking (default: True)
- `--vector-search`: Boolean - Enable vector search (default: True)
- `--keyword-search`: Boolean - Enable keyword search (default: False)
- `--graph-search`: Boolean - Enable graph search (default: True)
- `--help`: Boolean - Show help message

## Environment Variables

Required environment variables for system operation:

```
# QWen Configuration
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=sk-***

# Memgraph
DATABASE_URL=bolt://127.0.0.1:7687
DATABASE_USER=
DATABASE_PASSWORD=
```