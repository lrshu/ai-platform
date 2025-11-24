# RAG Backend System

A Retrieval-Augmented Generation (RAG) backend system with document indexing, hybrid search, and conversational question answering capabilities.

## Features

- **Document Indexing**: Parse PDF documents and create searchable indexes
- **Hybrid Search**: Combine vector similarity search with knowledge graph relationships
- **Conversational QA**: Chat with documents using context-aware responses
- **CLI Interface**: Simple command-line interface for all operations

## Architecture

The system follows a modular architecture with three main components:

1. **Indexing Pipeline**: Processes documents and creates searchable representations
2. **Search Pipeline**: Finds relevant content using hybrid retrieval methods
3. **Chat Pipeline**: Generates natural language responses based on retrieved content

For detailed architecture information, see [Architecture Documentation](docs/architecture.md).

## Prerequisites

- Python 3.12+
- Memgraph database
- DashScope API key for Qwen models

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rag-backend
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Usage

For detailed CLI usage and help information, see [CLI Help Documentation](docs/cli_help.md).

### Indexing Documents

```bash
python main.py indexing --name my_collection --file /path/to/document.pdf
```

### Searching Documents

```bash
python main.py search --name my_collection --question "What is this document about?"
```

### Chatting with Documents

```bash
python main.py chat --name my_collection --question "Can you explain the key points?"
```

## Configuration

The system is configured using environment variables in the `.env` file:

```env
# Qwen Configuration
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=your-api-key-here

# Memgraph Database
DATABASE_URL=bolt://127.0.0.1:7687
DATABASE_USER=
DATABASE_PASSWORD=
```

## Development

### Setting up Development Environment

1. Install uv package manager
2. Install dependencies: `uv sync`
3. Run tests: `pytest`

### Code Quality

- Code is formatted using ruff
- Linting is performed with ruff
- Type hints are encouraged

### Testing

Run all tests:
```bash
pytest
```

Run specific test suites:
```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# Contract tests
pytest tests/contract
```

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [CLI Help](docs/cli_help.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite
6. Submit a pull request

## License

[Specify your license here]

## Support

For issues and feature requests, please [open an issue](../../issues) on GitHub.