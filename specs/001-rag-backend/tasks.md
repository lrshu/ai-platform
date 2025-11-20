# Tasks: RAG Backend Implementation

**Input**: Design documents from `/specs/001-rag-backend/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story, following the RAG Backend Platform Constitution principles.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

For RAG backend implementations:
- **Source code**: `app/` at repository root (following constitution structure)
- **Tests**: `tests/` at repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure following RAG backend constitution

- [x] T001 Create project structure per implementation plan (following app/ directory structure)
- [x] T002 Initialize Python 3.12+ project with FastAPI, Pydantic V2, Memgraph, DashScope, Mineru dependencies
- [x] T003 [P] Configure linting and formatting tools (ruff, black, mypy)
- [x] T004 [P] Setup config.json5 with environment variable loading using json5 and python-dotenv
- [x] T005 [P] Create .env.example file with required environment variables
- [x] T006 [P] Setup pytest configuration with unit, integration, and contract test directories

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure components required by all user stories

- [x] T007 Create abstract base classes for all external service interfaces in app/common/interfaces/
- [x] T008 [P] Implement IDatabase interface in app/common/interfaces/database.py
- [x] T009 [P] Implement ITextGenerator interface in app/common/interfaces/generator.py
- [x] T010 [P] Implement IEmbedder interface in app/common/interfaces/embedder.py
- [x] T011 [P] Implement IReranker interface in app/common/interfaces/reranker.py
- [x] T012 [P] Implement IDocumentParser interface in app/common/interfaces/parser.py
- [x] T013 Create shared Pydantic models in app/common/models.py based on data-model.md
- [x] T014 [P] Implement SearchRequest model with validation rules
- [x] T015 [P] Implement Chunk model with embedding and metadata
- [x] T016 [P] Implement DocumentMetadata model with溯源 information
- [x] T017 [P] Implement Entity and Relationship models for graph storage
- [x] T018 [P] Implement GenerationResponse model for LLM outputs
- [x] T019 Implement configuration loader in app/common/config_loader.py with JSON5 parsing and env var overrides
- [x] T020 Create factory pattern for provider instantiation based on configuration

## Phase 3: User Story 1 - Document Indexing and Storage (Priority: P1)

**Goal**: As a system administrator, I want to index documents and store them in both vector and graph databases so that users can search through them later.

**Independent Test**: Can be fully tested by uploading a test document, triggering the indexing process, and verifying that both vector embeddings and graph entities are correctly stored in their respective databases.

- [x] T021 [US1] Implement MemgraphDB class in app/database/memgraph_db.py using gqlalchemy
- [x] T022 [P] [US1] Implement vector search functionality using Memgraph MAGE
- [x] T023 [P] [US1] Implement keyword search with Fulltext Index
- [x] T024 [P] [US1] Implement graph storage for nodes and edges
- [x] T025 [US1] Implement QwenProvider class in app/providers/qwen_provider.py using dashscope SDK
- [x] T026 [P] [US1] Implement embedding generation in QwenProvider
- [x] T027 [P] [US1] Implement MineruProvider class in app/providers/mineru_provider.py
- [x] T028 [P] [US1] Implement document parsing in MineruProvider
- [x] T029 [US1] Implement Small-to-Big chunking strategy in app/indexing/chunker.py
- [x] T030 [P] [US1] Implement parent chunk splitting (~1000 tokens)
- [x] T031 [P] [US1] Implement child chunk splitting (~200 tokens) with overlap
- [x] T032 [US1] Implement indexing orchestrator in app/indexing/orchestrator.py
- [x] T033 [P] [US1] Implement document parsing workflow
- [x] T034 [P] [US1] Implement chunking and embedding workflow
- [x] T035 [P] [US1] Implement storage workflow for vectors and graph
- [x] T036 [US1] Implement indexing API endpoint in app/api/indexing.py
- [x] T037 [P] [US1] Create unit tests for MemgraphDB vector storage
- [x] T038 [P] [US1] Create unit tests for QwenProvider embedding generation
- [x] T039 [P] [US1] Create unit tests for chunking implementation
- [x] T040 [US1] Create integration test for end-to-end indexing workflow

## Phase 4: User Story 2 - Basic Search and Retrieval (Priority: P2)

**Goal**: As an end user, I want to search for information using natural language queries so that I can find relevant document content.

**Independent Test**: Can be tested by submitting a search query and verifying that relevant document chunks are returned with appropriate similarity scores.

- [ ] T041 [US2] Implement HyDE (Hypothetical Document Embeddings) in app/retrieval/hyde.py
- [ ] T042 [P] [US2] Implement query expansion functionality
- [ ] T043 [US2] Implement MemgraphRetriever class in app/retrieval/memgraph_retriever.py
- [ ] T044 [P] [US2] Implement vector search in MemgraphRetriever
- [ ] T045 [P] [US2] Implement keyword search in MemgraphRetriever
- [ ] T046 [P] [US2] Implement hybrid search result merging
- [ ] T047 [US2] Implement context recall in app/post_retrieval/context_recall.py
- [ ] T048 [P] [US2] Implement parent chunk retrieval based on child results
- [ ] T049 [US2] Implement search API endpoint in app/api/search.py
- [ ] T050 [P] [US2] Create unit tests for HyDE implementation
- [ ] T051 [P] [US2] Create unit tests for MemgraphRetriever
- [ ] T052 [P] [US2] Create unit tests for context recall
- [ ] T053 [US2] Create integration test for basic search workflow

## Phase 5: User Story 3 - Enhanced Answer Generation (Priority: P3)

**Goal**: As an end user, I want to receive coherent answers generated by an LLM based on retrieved document context so that I don't have to read through documents myself.

**Independent Test**: Can be tested by submitting a question and verifying that a coherent, contextually relevant answer is generated and streamed back to the user.

- [ ] T054 [US3] Implement answer generation in QwenProvider in app/providers/qwen_provider.py
- [ ] T055 [P] [US3] Implement prompt assembly with document context
- [ ] T056 [US3] Implement reranking functionality in app/post_retrieval/reranker.py
- [ ] T057 [P] [US3] Implement gte-rerank integration with QwenProvider
- [ ] T058 [US3] Implement RAGPipeline class in app/orchestration/rag_pipeline.py
- [ ] T059 [P] [US3] Implement dynamic pipeline orchestration based on request parameters
- [ ] T060 [P] [US3] Implement conditional HyDE execution
- [ ] T061 [P] [US3] Implement conditional reranking execution
- [ ] T062 [US3] Implement streaming response in search API endpoint
- [ ] T063 [P] [US3] Create unit tests for answer generation
- [ ] T064 [P] [US3] Create unit tests for reranking functionality
- [ ] T065 [P] [US3] Create unit tests for RAGPipeline orchestration
- [ ] T066 [US3] Create integration test for end-to-end RAG workflow with streaming

## Phase 6: Cross-Cutting Concerns & Polish

**Purpose**: Production readiness, performance optimization, and documentation

- [ ] T067 Implement comprehensive error handling and HTTP error responses
- [ ] T068 [P] Add Google-style Docstrings with Type Hints to all public interfaces
- [ ] T069 [P] Implement logging and monitoring instrumentation
- [ ] T070 [P] Create Dockerfile optimized for Python 3.12 and uv
- [ ] T071 [P] Add health check endpoints for service monitoring
- [ ] T072 [P] Optimize database connection pooling
- [ ] T073 [P] Implement request validation and sanitization
- [ ] T074 [P] Add API documentation using FastAPI's automatic OpenAPI generation
- [ ] T075 [P] Create example client code and usage documentation
- [ ] T076 [P] Implement performance benchmarks for indexing and search
- [ ] T077 [P] Add retry logic and circuit breakers for external service calls
- [ ] T078 Run full suite of contract tests against OpenAPI specification

## Dependencies

User Story Implementation Order:
1. US1 (P1) - Document Indexing and Storage (No dependencies)
2. US2 (P2) - Basic Search and Retrieval (Depends on US1 for indexed data)
3. US3 (P3) - Enhanced Answer Generation (Depends on US2 for retrieval)

## Parallel Execution Opportunities

Each user story has multiple parallelizable tasks marked with [P]:
- US1: 8 parallelizable tasks (T022-T028, T030-T031, T033-T035, T037-T039)
- US2: 7 parallelizable tasks (T042, T044-T046, T048, T050-T052)
- US3: 8 parallelizable tasks (T055, T057, T059-T061, T063-T065)

## Implementation Strategy

MVP First Approach:
1. Start with User Story 1 (P1) to establish core indexing capability
2. Add User Story 2 (P2) for basic search functionality
3. Enhance with User Story 3 (P3) for full RAG experience
4. Polish with cross-cutting concerns for production readiness

Each phase delivers independently testable functionality, enabling incremental delivery and early validation.