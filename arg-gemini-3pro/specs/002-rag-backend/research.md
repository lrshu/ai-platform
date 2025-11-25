# Research: RAG Backend System

**Purpose**: To document best practices and decisions for the chosen technology stack.

## Decisions

### 1. LangChain for Orchestration

- **Decision**: Use LangChain's Expression Language (LCEL) to chain the different stages of the RAG pipeline (indexing, retrieval, generation).
- **Rationale**: LCEL provides a declarative and transparent way to build complex chains, making the pipeline easier to understand, debug, and modify. It also supports parallel execution for steps that can be run concurrently.
- **Alternatives considered**: A custom Python script to manually call each component. This was rejected as it would be more verbose and less maintainable.

### 2. Memgraph for Storage

- **Decision**: Use Memgraph to store both vector embeddings and the knowledge graph. Memgraph's `graph-algorithms` and `graph-machine-learning` libraries will be leveraged.
- **Rationale**: Storing vectors and the graph in the same database simplifies the architecture and allows for powerful hybrid search queries that combine semantic and graph-based retrieval in a single query.
- **Alternatives considered**: Using a separate vector database (e.g., FAISS, ChromaDB) and a graph database (e.g., Neo4j). This was rejected due to the complexity of managing two separate databases and synchronizing data between them.

### 3. Typer for CLI

- **Decision**: Use Typer to build the command-line interface.
- **Rationale**: Typer is modern, easy to use, and based on Python type hints. It automatically generates help messages and provides robust validation.
- **Alternatives considered**: `argparse`, `click`. Typer provides a better developer experience and is more concise for this project's needs.

## Open Questions

- **Q1**: What is the optimal chunking strategy for the given PDF documents?
  - **Decision**: Start with a recursive character text splitter with a chunk size of 1000 characters and an overlap of 200. This will be made configurable.
- **Q2**: How to best represent the knowledge graph schema in Memgraph?
  - **Decision**: Use a simple schema of `(:Entity {name: string})` and `[:RELATIONSHIP {type: string}]`. The entity and relationship types will be extracted using the LLM during the indexing phase.
