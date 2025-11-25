# CLI Contracts: RAG Backend System

This document defines the command-line interface for the RAG backend system.

## 1. `indexing`

Indexes a new PDF document into a specified knowledge base.

- **Command**: `python main.py indexing`
- **Arguments**:
    - `--name`: `string` (Required) - The name of the knowledge base.
    - `--file`: `path` (Required) - The path to the PDF file to index.
- **Example**:
    ```bash
    python main.py indexing --name my-knowledge-base --file /path/to/document.pdf
    ```

## 2. `search`

Performs a retrieval query against a knowledge base and returns the raw text chunks.

- **Command**: `python main.py search`
- **Arguments**:
    - `--name`: `string` (Required) - The name of the knowledge base.
    - `--question`: `string` (Required) - The question to ask.
- **Options**:
    - `--no-expand-query`: `bool` (Flag) - Disable query expansion.
    - `--no-rerank`: `bool` (Flag) - Disable result re-ranking.
- **Example**:
    ```bash
    python main.py search --name my-knowledge-base --question "What is LangChain?"
    ```

## 3. `chat`

Performs a conversational query against a knowledge base and returns a generated answer.

- **Command**: `python main.py chat`
- **Arguments**:
    - `--name`: `string` (Required) - The name of the knowledge base.
    - `--question`: `string` (Required) - The question to ask.
- **Options**:
    - `--no-expand-query`: `bool` (Flag) - Disable query expansion.
    - `--no-rerank`: `bool` (Flag) - Disable result re-ranking.
- **Example**:
    ```bash
    python main.py chat --name my-knowledge-base --question "Can you explain LangChain to me?"
    ```
