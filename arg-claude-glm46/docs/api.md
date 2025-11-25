# API Documentation

## CLI Commands

### Indexing

Index a PDF document for search and QA.

```bash
python main.py indexing --name <document_name> --file <file_path>
```

**Parameters:**
- `--name`: Unique identifier for the document
- `--file`: Path to the PDF file to be indexed

**Example:**
```bash
python main.py indexing --name "research_paper" --file "./papers/research.pdf"
```

### Search

Search for information within indexed documents.

```bash
python main.py search --name <document_name> --question <query> [--top-k <n>] [--expand-query] [--rerank]
```

**Parameters:**
- `--name`: Name of the document collection to search
- `--question`: The question or query to search for
- `--top-k`: Number of results to return (default: 5)
- `--expand-query`: Enable query expansion
- `--rerank`: Enable result re-ranking

**Example:**
```bash
python main.py search --name "research_paper" --question "What is the main finding?" --top-k 3 --expand-query --rerank
```

### Chat

Engage in conversational QA with indexed documents.

```bash
python main.py chat --name <document_name> [--user-id <user_id>]
```

**Parameters:**
- `--name`: Name of the document collection to use
- `--user-id`: User identifier (optional, defaults to "default_user")

**Example:**
```bash
python main.py chat --name "research_paper" --user-id "researcher123"
```

## Service APIs

### Indexing Service

The indexing service processes documents through multiple stages:

1. **Parsing**: Extracts text content from PDF documents
2. **Chunking**: Splits content into manageable chunks
3. **Embedding**: Generates vector embeddings for each chunk
4. **Knowledge Graph Extraction**: Identifies entities and relationships
5. **Storage**: Saves all data to the database

### Search Service

The search service performs hybrid search combining:

1. **Vector Search**: Finds semantically similar content using embeddings
2. **Graph Search**: Leverages knowledge graph relationships
3. **Result Combination**: Merges and ranks results from both approaches
4. **Re-ranking**: Optionally re-ranks results using LLM-based relevance

### Conversation Service

The conversation service manages interactive dialogues:

1. **Context Management**: Maintains conversation history
2. **Query Processing**: Processes user messages
3. **Response Generation**: Generates context-aware responses
4. **Session Management**: Handles conversation lifecycle

## Error Handling

The system uses structured error handling with specific exception types:

- `DocumentProcessingError`: Issues with document parsing or processing
- `DatabaseError`: Problems with database operations
- `LLMError`: Errors from language model services
- `EmbeddingError`: Issues with embedding generation

All errors are logged with context information for debugging.