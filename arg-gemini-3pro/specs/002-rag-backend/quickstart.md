# Quickstart: RAG Backend System

This guide provides instructions on how to set up and run the RAG backend system.

## 1. Prerequisites

- Python 3.12+
- `uv` installed (`pip install uv`)
- Docker and Docker Compose

## 2. Setup

### a. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### b. Create the environment file

Create a `.env` file in the root of the project with the following content:

```env
# QWen Configuration
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY="sk-..."

# Memgraph
DATABASE_URL="bolt://127.0.0.1:7687"
DATABASE_USER=""
DATABASE_PASSWORD=""
```

### c. Install dependencies

```bash
uv pip install -r requirements.txt
```

### d. Start Memgraph

A `docker-compose.yml` file will be provided to easily start a Memgraph instance.

```bash
docker-compose up -d
```

## 3. Usage

### a. Index a document

```bash
python main.py indexing --name my-knowledge-base --file /path/to/your/document.pdf
```

### b. Search for information

```bash
python main.py search --name my-knowledge-base --question "What is the main topic of the document?"
```

### c. Chat with the document

```bash
python main.py chat --name my-knowledge-base --question "Can you summarize the document for me?"
```
