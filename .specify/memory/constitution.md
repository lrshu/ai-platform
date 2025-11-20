<!--
Sync Impact Report:
Version change: 1.0.0 → 1.1.0
Modified principles: None (new constitution)
Added sections: All sections (new constitution)
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
Follow-up TODOs: None
-->

# RAG Backend Platform Constitution

## Core Principles

### I. Modular Architecture
The highest guiding principle is to build a highly modular, decoupled, and observable RAG backend. The system architecture strictly follows the "Modular RAG" paradigm, standardizing the processing pipeline into six pipeline stages: Indexing, Pre-Retrieval, Retrieval, Post-Retrieval, Generation, and Orchestration. All data flows must pass through these standardized stages, never skipping core abstractions to directly call underlying logic.

### II. Pipeline Stages Standardization
Every RAG workflow must flow through these six standardized stages:
1. Indexing: Parse → Split → Embed → Store (Graph + Vector)
2. Pre-Retrieval: Query understanding and rewriting (HyDE, Query Expansion)
3. Retrieval: Multi-path recall (Hybrid Search)
4. Post-Retrieval: Context optimization (Rerank, Selection)
5. Generation: Prompt assembly and LLM inference
6. Orchestration: Dynamic module scheduling controlled by user requests

Each stage must be implemented as independent modules with clear interfaces.

### III. Provider Abstraction
External services must be defined as capability providers implementing specific capability interfaces. This abstraction layer ensures loose coupling and easy substitution of external services. Capability interfaces (ITextGenerator, IEmbedder, IReranker, IDocumentParser, etc.) are unified in the app/common/interfaces/ module.

### IV. Configuration-Driven Architecture
Core RAG logic dynamically obtains required capability provider instances and specific model names through configuration. All configurations (including sensitive information) must be loaded through config.json5, with sensitive API keys loaded at runtime via environment variables.

### V. Documentation and Code Quality
Core functions must include Google-style Docstrings with Type Hints. Each module must follow the Single Responsibility Principle, encapsulating each stage (such as HyDEGenerator, MemgraphRetriever) as an independent class.

## Technology Stack Requirements

### Runtime and Dependencies
- Runtime: Python 3.12+
- Dependency Manager: uv (for极致 speed)
- Web Framework: FastAPI (全异步模式 with async/await)
- Data Validation: Pydantic V2

### Database and Model Providers
- Database (Vector + Graph): Memgraph (utilizing its Graph & Vector capabilities)
- Primary Model Provider: Qwen/DashScope
- LLM Models: Qwen-Turbo/Plus/Max
- Embedding Models: text-embedding-v4
- Reranking Models: gte-rerank
- Document Parsing Provider: Mineru API

## Development Workflow

### Directory Structure
```
app/
├── api/                 # API Gateway & Endpoints
├── common/              # Core Infrastructure
│   ├── interfaces/      # Abstract Base Classes
│   │   ├── database.py
│   │   ├── generator.py
│   │   ├── embedder.py
│   │   ├── reranker.py
│   │   ├── parser.py
│   ├── config_loader.py
│   ├── models.py        # Shared Pydantic Models
│   ├── utils.py
├── database/            # Memgraph Implementation
├── indexing/            # Indexing Logic
├── retrieval/           # Retrieval Logic (Pre & Core)
├── post_retrieval/      # Post-Retrieval Logic
├── generation/          # Generation Logic
├── providers/           # External Service Providers
├── orchestration/       # Pipeline & Orchestrator
config.json5             # Main Configuration
pyproject.toml
main.py
```

### Implementation Guidelines
1. All external service integrations must implement corresponding provider interfaces
2. Modules must be independently testable with clear input/output contracts
3. Follow Test-First development approach with comprehensive unit and integration tests
4. All API endpoints must include proper error handling and logging
5. Code reviews must verify compliance with these constitutional principles

## Governance

This Constitution supersedes all other development practices and guidelines. Any amendments must be documented with clear justification and implementation plan.

All pull requests and code reviews must verify compliance with these principles. Complexity must be justified with clear rationale. Use README.md and other documentation files for runtime development guidance.

**Version**: 1.1.0 | **Ratified**: 2025-11-20 | **Last Amended**: 2025-11-20