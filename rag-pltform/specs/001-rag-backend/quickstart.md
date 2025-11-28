# Quickstart Guide: RAG Backend System

## Prerequisites

1. Python 3.12+ installed
2. uv package manager installed
3. Memgraph database running
4. DashScope API key for Qwen models

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd rag-backend
   ```

2. Install dependencies using uv:
   ```
   uv sync
   ```

3. Set up environment variables by creating a `.env` file:
   ```
   # QWen Configuration
   QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_API_KEY=your-api-key-here

   # Memgraph
   DATABASE_URL=bolt://127.0.0.1:7687
   DATABASE_USER=
   DATABASE_PASSWORD=
   ```

## Quick Start

1. Index a PDF document:
   ```
   python main.py indexing --name mydoc --file /path/to/document.pdf
   ```

2. Search the indexed document:
   ```
   python main.py search --name mydoc --question "What is this document about?"
   ```

3. Chat with the document:
   ```
   python main.py chat --name mydoc
   ```

## Project Structure

```
src/
├── models/          # Data models
├── services/        # Business logic
├── cli/             # Command-line interface
└── lib/             # Utility functions

tests/
├── unit/            # Unit tests
├── integration/     # Integration tests
└── contract/        # Contract tests
```

## Configuration

The system is configured through environment variables in a `.env` file. Key configuration options include:

- `QWEN_API_KEY`: Your DashScope API key for Qwen models
- `DATABASE_URL`: Connection string for Memgraph database
- `DATABASE_USER`: Database username (if required)
- `DATABASE_PASSWORD`: Database password (if required)

## Testing

Run all tests:
```
pytest
```

Run specific test types:
```
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Contract tests only
pytest tests/contract/
```

## Development

1. Create a feature branch:
   ```
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests to ensure nothing is broken:
   ```
   pytest
   ```

4. Commit your changes:
   ```
   git commit -am "Add your feature description"
   ```

5. Push and create a pull request:
   ```
   git push origin feature/your-feature-name
   ```

## Troubleshooting

### Common Issues

1. **Database connection failed**: Ensure Memgraph is running and connection details are correct in `.env`

2. **API key invalid**: Verify your Qwen API key is correct and has sufficient credits

3. **PDF parsing errors**: Ensure the PDF file is not corrupted and is a valid PDF format

### Getting Help

For issues not covered in this guide, please:
1. Check the logs for detailed error messages
2. Refer to the full documentation
3. Contact the development team