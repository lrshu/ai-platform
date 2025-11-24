# Quickstart Guide: RAG Backend System

This guide will help you get started with the RAG backend system, covering installation, setup, and basic usage.

## Prerequisites

- Python 3.12+
- uv package manager
- Memgraph database running on localhost:7687
- DashScope API key for Qwen models

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Create a `.env` file with your configuration:
   ```env
   # QWen Configuration
   QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_API_KEY="your-api-key-here"

   # Memgraph
   DATABASE_URL="bolt://127.0.0.1:7687"
   DATABASE_USER=""
   DATABASE_PASSWORD=""
   ```

## Usage

### 1. Indexing Documents

To index a PDF document:

```bash
python main.py indexing --name my_collection --file /path/to/document.pdf
```

This command will:
- Parse the PDF document
- Split it into chunks
- Generate vector embeddings for each chunk
- Extract entities and relationships to build a knowledge graph
- Store all data in Memgraph under the specified collection name

### 2. Searching Documents

To search for information in indexed documents:

```bash
python main.py search --name my_collection --question "What is the main topic of the document?"
```

This command will:
- Expand the query (if enabled)
- Perform hybrid retrieval (vector + graph search)
- Re-rank results (if enabled)
- Return the most relevant document chunks

### 3. Chatting with Documents

To have a conversation about indexed documents:

```bash
python main.py chat --name my_collection --question "Can you summarize the key points?"
```

This command will:
- Retrieve relevant content based on your question
- Generate a coherent answer using the Qwen3-Max LLM
- Maintain conversation context for follow-up questions

## Configuration Options

You can customize the behavior of each command with additional options:

### Indexing Options
- `--name`: Collection name (required)
- `--file`: Path to PDF file (required)

### Search Options
- `--name`: Collection name (required)
- `--question`: Query text (required)
- `--top-k`: Number of results to return (default: 5)
- `--no-expand`: Disable query expansion
- `--no-rerank`: Disable result re-ranking
- `--no-vector`: Disable vector search
- `--no-graph`: Disable graph search

### Chat Options
- `--name`: Collection name (required)
- `--question`: Query text (required)
- `--session-id`: Session identifier for context (optional)
- `--top-k`: Number of results to return (default: 5)
- `--no-expand`: Disable query expansion
- `--no-rerank`: Disable result re-ranking
- `--no-vector`: Disable vector search
- `--no-graph`: Disable graph search

## Example Workflow

1. Index a document:
   ```bash
   python main.py indexing --name research_papers --file ~/documents/paper.pdf
   ```

2. Search for information:
   ```bash
   python main.py search --name research_papers --question "What methodology was used?"
   ```

3. Have a conversation:
   ```bash
   python main.py chat --name research_papers --question "Can you explain the results in simpler terms?"
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**: Ensure Memgraph is running on localhost:7687
2. **API Key Error**: Verify your DashScope API key is correct and has sufficient quota
3. **File Not Found**: Check that the file path is correct and accessible
4. **Memory Issues**: For large documents, consider increasing system memory or processing in smaller chunks

### Getting Help

For additional help, use the `--help` flag with any command:
```bash
python main.py --help
python main.py indexing --help
python main.py search --help
python main.py chat --help
```

## Next Steps

- Explore advanced configuration options
- Review the data model documentation
- Check the API contracts for integration possibilities
- Run the test suite to ensure everything is working correctly