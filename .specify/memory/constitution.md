<!--
Sync Impact Report:
- Version change: 1.1.0 → 1.2.0 (minor update with detailed architecture, provider abstraction, and configuration management)
- Modified principles: Pipeline Architecture (I), Technology Stack (II), Provider Abstraction (III), Documentation First (IV), Configuration Management (VI)
- Added sections: Provider Abstraction and Modular Design principle (III), Configuration Management principle (VI)
- Removed sections: None
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md (updated Constitution Check section)
  ✅ .specify/templates/spec-template.md (aligned with modular RAG principles)
  ✅ .specify/templates/tasks-template.md (aligned with documentation-first principle)
- Deferred items: None
-->

# Modular RAG AI Knowledge Base Platform Constitution

## Core Principles

### I. Pipeline Architecture
The system MUST strictly follow the six-stage pipeline with specific responsibilities:

1. **Indexing**: Parse → Chunk → Embed → Store (Graph + Vector)
2. **Pre-Retrieval**: Query understanding and rewriting (HyDE, Query Expansion)
3. **Retrieval**: Multi-path recall (Hybrid Search)
4. **Post-Retrieval**: Context optimization (Rerank, Selection)
5. **Generation**: Prompt assembly and LLM reasoning
6. **Orchestration**: Dynamic module scheduling controlled by user requests

Each stage must be independently testable and maintain clear boundaries. Direct calls to underlying logic that bypass core abstractions are strictly prohibited. This architecture enables modularity, scalability, and maintainability of the RAG system.

### II. Technology Stack
The system MUST use the following technology stack:
- Runtime: Python 3.12+
- Dependency Manager: uv (for极致 speed)
- Web Framework: FastAPI (全异步模式 with async/await)
- Data Validation: Pydantic V2
- Database (Vector + Graph): Memgraph
- Model Provider (Primary): Aliyun Bailian (Qwen/DashScope)
- LLM: Qwen-Turbo/Plus/Max
- Embedding: text-embedding-v4
- Rerank: gte-rerank
- Doc Parsing Provider: Mineru API
Any deviation from this stack requires explicit justification and approval through the governance process.

### III. Provider Abstraction and Modular Design
External services MUST be defined as capability providers that implement specific capability interfaces. This abstraction layer ensures loose coupling and easy substitution of implementations.

**Capability Interfaces**: ITextGenerator, IEmbedder, IReranker, IDocumentParser

**Providers**:
- QwenProvider (implements 3 model capabilities: text generation, embedding, reranking)
- MineruProvider (implements document parsing capability)

Each pipeline stage (such as HyDEGenerator, MemgraphRetriever) MUST be encapsulated as an independent class following the single responsibility principle. Components MUST be orchestrated through a central Orchestrator rather than direct coupling. Spaghetti code and tight coupling between stages are strictly prohibited.

Core RAG logic MUST dynamically obtain required capability provider instances and specific model names through configuration. This approach enables flexible composition and testing of different provider combinations.

### IV. Documentation First
Core functions MUST include Google-style docstrings with comprehensive type hints before implementation begins. Public APIs, service interfaces, and complex algorithms MUST be documented with clear examples and expected behaviors. This principle ensures code maintainability and enables effective collaboration.

### V. Bilingual Documentation
All markdown documentation MUST be provided in both Chinese and English, with Chinese as the primary language. Documentation files MUST follow the naming convention: **.md for Chinese content and **.en.md for English content. This requirement ensures accessibility for both local and international team members and users.

### VI. Configuration Management
All configuration (including sensitive information) MUST be loaded through a config.json5 file. Sensitive API Keys and other confidential configuration MUST be overridden or loaded through environment variables at runtime. Core RAG logic MUST dynamically obtain required capability provider instances and specific model names through configuration.

## Technology Stack

### Required Technologies
- **Runtime**: Python 3.12+ for advanced async support and modern language features
- **Dependency Manager**: uv for极致 speed (替代 pip/poetry)
- **Framework**: FastAPI 全异步模式 with async/await for high-performance web services
- **Validation**: Pydantic V2 for data validation and settings management
- **Database (Vector + Graph)**: Memgraph for both vector storage and graph relationships
- **Model Provider (Primary)**: Aliyun Bailian (Qwen/DashScope)
- **LLM Models**: Qwen-Turbo/Plus/Max
- **Embedding Model**: text-embedding-v4
- **Rerank Model**: gte-rerank
- **Doc Parsing Provider**: Mineru API

### Optional Integrations
- Monitoring: Prometheus/Grafana for metrics collection
- Logging: Structured logging with JSON format for better observability
- CI/CD: GitHub Actions or equivalent for automated testing and deployment

## Development Workflow

### Code Organization
- Each pipeline stage MUST be implemented in its own module
- Shared utilities MUST be placed in common libraries
- Configuration MUST be externalized and environment-aware
- All APIs MUST follow RESTful principles with clear resource-oriented design

### Review Process
- All code changes MUST be reviewed by at least one other team member
- Pull requests MUST include updated documentation for any public-facing changes
- Automated checks MUST pass before merging (linting, testing, security scanning)
- Complex architectural changes MUST be discussed in design sessions before implementation

### Quality Gates
- Unit test coverage MUST be ≥80% for new code
- All PRs MUST pass automated CI pipeline
- Security scans MUST pass with no critical vulnerabilities
- Performance benchmarks MUST meet defined SLAs for query response times

## Governance

### Amendment Process
This constitution serves as the foundational document for the project. Any amendments MUST follow this process:
1. Proposal submission with clear justification
2. Community review period of at least 7 days
3. Approval by 2/3 majority of core maintainers
4. Update to dependent templates and documentation
5. Communication to all stakeholders

### Versioning Policy
Constitution versions follow semantic versioning:
- MAJOR: Backward incompatible governance changes or principle removals
- MINOR: New principles or materially expanded guidance
- PATCH: Clarifications, wording improvements, non-semantic refinements

### Compliance Review
All project deliverables MUST be verified against constitutional principles:
- Architecture reviews MUST confirm pipeline adherence
- Code reviews MUST validate modular decoupling
- Documentation reviews MUST ensure completeness
- Testing MUST cover all core principles

**Version**: 1.2.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19