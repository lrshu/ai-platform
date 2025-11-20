<!-- Sync Impact Report:
Version change: 1.0.0
Modified principles: None (initial version)
Added sections: All sections (initial version)
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
Deferred items: None
-->

# RAG Backend Platform Constitution

## Core Principles

### I. Modular Architecture
The system must be built with a highly modular, decoupled, and observable architecture. The system architecture strictly follows the "Modular RAG" paradigm, standardizing the processing pipeline into six stages.

### II. Standardized Pipeline Stages
All data flows must go through the following standardized stages, and skipping core abstractions to directly call underlying logic is strictly prohibited:

1. Indexing (Parsing → Chunking → Embedding → Storage (Graph + Vector))
2. Pre-Retrieval (Query Understanding and Rewriting)
3. Retrieval (Multi-path Recall)
4. Post-Retrieval (Context Optimization)
5. Generation (Prompt Assembly and LLM Reasoning)
6. Orchestration (Dynamic Module Scheduling)

### III. Technology Stack Requirements
Runtime: Python 3.12+
Dependency Management: uv (replacing pip/poetry for maximum speed)
Web Framework: FastAPI with full async/await pattern
Validation: Pydantic V2 for data validation and model definition
Database: Memgraph leveraging its Graph & Vector capabilities
LLM Provider: Aliyun Bailian (DashScope) as the primary model service provider
Models: Qwen-Turbo/Plus/Max for generation and knowledge extraction
Embedding: text-embedding-v4 for vectorization
Reranking: gte-rerank
Parsing: Mineru API document parsing service

### IV. Provider Abstraction and Dependency Injection
External services must be defined as capability providers implementing specific capability interfaces. Core RAG logic depends only on interfaces. Modules must receive interface instances and specific model names specified in configuration through dependency injection.

### V. Code Quality Standards
Core functions must include Google-style Docstrings and Type Hints. All code must follow consistent formatting and style guidelines.

## Unified Directory Structure
The project follows a unified directory structure:
```
backend/
├── app/
│   ├── api/                # API Gateway & Endpoints
│   ├── common/             # Core Infrastructure
│   │   ├── interfaces/     # Abstract Base Classes
│   │   │   ├── database.py
│   │   │   ├── generator.py
│   │   │   ├── embedder.py
│   │   │   ├── reranker.py
│   │   │   ├── parser.py
│   │   ├── config_loader.py
│   │   ├── models.py       # Shared Pydantic Models
│   │   ├── utils.py
│   ├── database/           # Memgraph Implementation
│   ├── indexing/           # Indexing Logic
│   ├── retrieval/          # Retrieval Logic (Pre & Core)
│   ├── post_retrieval/     # Post-Retrieval Logic
│   ├── generation/         # Generation Logic
│   ├── providers/          # External Service Providers
│   ├── orchestration/      # Pipeline & Orchestrator
├── config.json5            # Main Configuration
├── pyproject.toml
└── main.py
```

## Development Workflow
All development must follow the Speckit methodology with specification, planning, and task-based implementation. Features are developed with prioritized user stories that can be independently tested and deployed. Code reviews are mandatory for all changes, with special attention to constitutional compliance.

## Governance
Constitution supersedes all other practices. Amendments require documentation, approval, and migration plan. All PRs/reviews must verify constitutional compliance. Versioning follows semantic versioning rules with MAJOR for backward incompatible changes, MINOR for new principles, and PATCH for clarifications.

**Version**: 1.0.0 | **Ratified**: 2025-11-20 | **Last Amended**: 2025-11-20