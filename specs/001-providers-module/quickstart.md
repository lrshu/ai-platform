# Quickstart Guide: Providers Module

## Overview

The Providers Module implements external service capabilities for the RAG pipeline while isolating API call details, authentication, and error handling from the core logic. This module acts as a firewall between the RAG core logic and external services.

## Prerequisites

- Python 3.12+
- uv package manager
- Access to Qwen and Mineru APIs
- Memgraph database (for logging and monitoring)

## Installation

1. Install dependencies using uv:
```bash
uv pip install -r pyproject.toml
```

2. Set up environment variables:
```bash
export QWEN_API_KEY="your_qwen_api_key"
export MINERU_API_KEY="your_mineru_api_key"
```

## Configuration

Create a `config.json5` file in the project root:

```json5
{
  // Database configuration
  "database": {
    "uri": "bolt://localhost:7687",
    "user": "memgraph",
    "password": "password"
  },

  // Core RAG pipeline capability configuration
  "pipeline_capabilities": {
    // Embedding capability configuration
    "embedder": {
      "provider": "Qwen",
      "name": "text-embedding-v4"
    },
    // LLM Generator/HyDE/Expansion capability configuration
    "generator": {
      "provider": "Qwen",
      "name": "qwen-plus"
    },
    // Rerank capability configuration
    "reranker": {
      "provider": "Qwen",
      "name": "gte-rerank"
    },
    // Document parsing capability configuration
    "parser": {
      "provider": "Mineru",
      "name": "v1"
    }
  },

  // Provider implementation class mapping
  "provider_map": {
    "Qwen": "app.providers.qwen_provider.QwenProvider",
    "Mineru": "app.providers.mineru_provider.MineruProvider"
  }
}
```

## Usage

### Initializing Providers

```python
from app.common.config_loader import load_config
from app.common.interfaces import ITextGenerator, IEmbedder, IReranker, IDocumentParser

# Load configuration
config = load_config()

# Initialize providers
qwen_provider = config.get_provider("Qwen")
mineru_provider = config.get_provider("Mineru")

# Get specific capability instances
text_generator = qwen_provider.get_capability(ITextGenerator)
embedder = qwen_provider.get_capability(IEmbedder)
reranker = qwen_provider.get_capability(IReranker)
document_parser = mineru_provider.get_capability(IDocumentParser)
```

### Using ITextGenerator

```python
# Generate text using the LLM
request = {
    "prompt": "Explain the concept of Retrieval Augmented Generation",
    "max_tokens": 500,
    "temperature": 0.7
}

response = text_generator.generate(request)
print(response.generated_text)
```

### Using IEmbedder

```python
# Generate embeddings for text
request = {
    "text": "Retrieval Augmented Generation combines retrieval and generation",
    "model": "text-embedding-v4"
}

response = embedder.embed(request)
print(response.embeddings)
```

### Using IReranker

```python
# Rerank documents based on relevance to query
request = {
    "query": "What is RAG?",
    "documents": [
        "Retrieval Augmented Generation combines retrieval and generation",
        "Large Language Models are powerful AI systems",
        "RAG improves LLM responses with external knowledge"
    ],
    "top_n": 2
}

response = reranker.rerank(request)
for result in response.results:
    print(f"Document: {result.document}, Score: {result.score}")
```

### Using IDocumentParser

```python
# Parse document content
with open("document.pdf", "rb") as f:
    document_content = f.read()

request = {
    "document_content": document_content,
    "document_type": "pdf"
}

response = document_parser.parse(request)
print(response.extracted_text)
```

## Error Handling

All providers implement comprehensive error handling:

```python
try:
    response = text_generator.generate(request)
except Exception as e:
    print(f"Error occurred: {e}")
    # Handle error appropriately
```

## Testing

Run tests using pytest:

```bash
pytest tests/
```

## Logging

All provider interactions are logged for monitoring and debugging. Logs include:
- Timestamp of each call
- Provider name
- Method and endpoint called
- Response status and time
- Error messages (if any)

## Performance Considerations

- Text generation response time target: under 2 seconds for 95% of requests
- Implement retry logic for transient failures
- Use connection pooling for HTTP requests
- Handle rate limiting appropriately