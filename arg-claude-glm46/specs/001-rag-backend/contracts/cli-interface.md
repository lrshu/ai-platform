# CLI Interface Contract

## Command: indexing

**Usage**: `python main.py indexing --name [name] --file [file_path]`

**Description**: Processes a PDF document through the indexing pipeline, extracting content, chunking it, generating embeddings and knowledge graph information, and storing everything in the database.

**Parameters**:
- `--name` (required): Unique name identifier for the document
- `--file` (required): Path to the PDF file to be indexed

**Output**:
- Success: Document ID and confirmation message
- Failure: Error message with details

**Exit Codes**:
- 0: Success
- 1: General error
- 2: File not found
- 3: Processing error

## Command: search

**Usage**: `python main.py search --name [name] --question [question]`

**Description**: Searches for relevant information within indexed documents by processing the question through the retrieval pipeline.

**Parameters**:
- `--name` (required): Name identifier of the document collection to search
- `--question` (required): The question to search for

**Options**:
- `--top-k` (optional, default=5): Number of results to return
- `--expand-query` (optional, flag): Enable query expansion
- `--rerank` (optional, flag): Enable result reranking

**Output**:
- Success: List of relevant content chunks with similarity scores
- Failure: Error message with details

**Exit Codes**:
- 0: Success
- 1: General error
- 4: No results found

## Command: chat

**Usage**: `python main.py chat --name [name]`

**Description**: Engages in a conversational question-answering session using indexed documents as context.

**Parameters**:
- `--name` (required): Name identifier of the document collection to use

**Options**:
- `--top-k` (optional, default=5): Number of results to consider for context
- `--expand-query` (optional, flag): Enable query expansion
- `--rerank` (optional, flag): Enable result reranking

**Interaction**:
- Starts interactive session
- User inputs questions
- System provides answers based on document content
- Session continues until user exits (Ctrl+C or 'quit')

**Output**:
- For each question: Generated answer based on retrieved context
- Session start/end messages

**Exit Codes**:
- 0: Success
- 1: General error
- 5: Conversation error