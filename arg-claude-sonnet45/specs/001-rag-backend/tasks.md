# Tasks: RAG Backend System

**Input**: Design documents from `/specs/001-rag-backend/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL per constitution - only include contract and integration tests if explicitly required for critical paths (80% coverage target).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (as per plan.md)
- All paths relative to project root: `/Users/zhengliu/Desktop/workspace/work/study/arg-claude-v5/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project source structure per plan.md (src/rag/, src/storage/, src/models/, src/cli/, src/config/)
- [ ] T002 Create test structure (tests/contract/, tests/integration/, tests/unit/)
- [ ] T003 [P] Initialize pyproject.toml with dependencies (LangChain, Chroma, neo4j, pymupdf4llm, dashscope, pydantic-settings)
- [ ] T004 [P] Create .env.example template with required environment variables (QWEN_API_KEY, DATABASE_URL)
- [ ] T005 [P] Create .gitignore (include .env, __pycache__, .venv, data/)
- [ ] T006 [P] Set up ruff configuration in pyproject.toml for linting and formatting
- [ ] T007 [P] Create logging configuration with JSON formatter in src/config/logging.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create Settings class with pydantic-settings in src/config/settings.py (loads .env, validates required vars)
- [ ] T009 [P] Create Document model (Pydantic) in src/models/document.py (id, name, filename, file_path, upload_timestamp, processing_status, chunk_count, error_message)
- [ ] T010 [P] Create DocumentChunk model (Pydantic) in src/models/document.py (id, document_id, text, embedding, position, char_offset, metadata)
- [ ] T011 [P] Create Query and QueryOptions models in src/models/query.py (id, document_name, original_text, expanded_text, timestamp, options with top_k, expand_query flags)
- [ ] T012 [P] Create RetrievalResult and RetrievedChunk models in src/models/query.py
- [ ] T013 [P] Create GeneratedResponse and Citation models in src/models/query.py
- [ ] T014 [P] Initialize Chroma client wrapper in src/storage/vector_store.py (create/get collections, add/query documents)
- [ ] T015 [P] Initialize Memgraph connection wrapper in src/storage/graph_store.py (Neo4j driver, connection pooling)
- [ ] T016 Create Memgraph schema initialization in src/storage/graph_store.py (Document and Chunk nodes, CONTAINS relationship, indexes)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Document Ingestion and Indexing (Priority: P1) 🎯 MVP

**Goal**: Users can upload PDF documents, which are parsed, chunked, embedded, and stored for retrieval

**Independent Test**: Upload a PDF via CLI, verify it's indexed in Chroma and Memgraph with correct chunk count and metadata

### Tests for User Story 1 (Contract Tests - Critical Path)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US1] Contract test for CLI indexing command in tests/contract/test_cli_indexing.py (verify exit codes, output format, error handling)
- [ ] T018 [P] [US1] Integration test for end-to-end indexing flow in tests/integration/test_indexing_flow.py (PDF → markdown → chunks → embeddings → storage)

### Implementation for User Story 1

- [ ] T019 [P] [US1] Implement parse_pdf() function in src/rag/indexing.py (uses pymupdf4llm.to_markdown, handles FileNotFoundError, ValueError for invalid PDFs)
- [ ] T020 [P] [US1] Implement chunk_text() function in src/rag/indexing.py (RecursiveCharacterTextSplitter, configurable chunk_size and overlap)
- [ ] T021 [US1] Implement embed_chunks() function in src/rag/indexing.py (batch embedding via DashScope text-embedding-v4, retry logic, error handling)
- [ ] T022 [US1] Implement store_document() in src/rag/indexing.py (create Chroma collection, insert chunks with embeddings and metadata, store Document and Chunk nodes in Memgraph)
- [ ] T023 [US1] Implement index_document() orchestration in src/rag/orchestration.py (coordinate parse → chunk → embed → store pipeline, return document_id)
- [ ] T024 [US1] Implement CLI indexing command in src/cli/main.py (argparse subcommand, call index_document(), format output, handle --json flag)
- [ ] T025 [US1] Add progress indicator for indexing operations >2 seconds in src/cli/main.py
- [ ] T026 [US1] Add structured logging for each indexing stage (parse, chunk, embed, store) with timing

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Basic Query and Retrieval (Priority: P2)

**Goal**: Users can submit natural language queries and receive relevant document chunks ranked by similarity

**Independent Test**: Submit query via CLI search command, verify top-K chunks returned with similarity scores and source references

### Tests for User Story 2 (Contract Tests - Critical Path)

- [ ] T027 [P] [US2] Contract test for CLI search command in tests/contract/test_cli_search.py (verify argument handling, output format, error cases)
- [ ] T028 [P] [US2] Integration test for retrieval flow in tests/integration/test_retrieval_flow.py (query → embedding → vector/keyword/graph search → merged results)

### Implementation for User Story 2

- [ ] T029 [P] [US2] Implement get_query_embedding() in src/rag/retrieval.py (generate query embedding using DashScope)
- [ ] T030 [P] [US2] Implement vector_search() in src/rag/retrieval.py (query Chroma collection, return top-K chunks with similarity scores)
- [ ] T031 [P] [US2] Implement keyword_search() in src/rag/retrieval.py (Cypher full-text search on Chunk.text in Memgraph, BM25-style scoring)
- [ ] T032 [P] [US2] Implement graph_search() stub in src/rag/retrieval.py (returns empty list for MVP, placeholder for future entity-based retrieval)
- [ ] T033 [US2] Implement hybrid_search() in src/rag/retrieval.py (run vector, keyword, graph searches in parallel if enabled, merge and deduplicate results)
- [ ] T034 [US2] Implement search_documents() orchestration in src/rag/orchestration.py (coordinate query processing and hybrid search)
- [ ] T035 [US2] Implement CLI search command in src/cli/main.py (argparse subcommand, call search_documents(), format output with --json support)
- [ ] T036 [US2] Add result formatting with similarity scores and source metadata in src/cli/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (semantic search system)

---

## Phase 5: User Story 3 - Answer Generation from Retrieved Context (Priority: P3)

**Goal**: Users receive natural language answers with source citations, not just raw chunks

**Independent Test**: Submit question via CLI chat command, verify coherent answer generated with citations to source chunks

### Tests for User Story 3 (Integration Tests - Critical Path)

- [ ] T037 [P] [US3] Contract test for CLI chat command in tests/contract/test_cli_chat.py (verify interactive loop, exit commands, output format)
- [ ] T038 [P] [US3] Integration test for end-to-end RAG flow in tests/integration/test_end_to_end.py (query → retrieval → generation → response with citations)

### Implementation for User Story 3

- [ ] T039 [P] [US3] Create LLM client wrapper in src/rag/generation.py (ChatOpenAI with Qwen API base, temperature=0.1, max_tokens=2000)
- [ ] T040 [US3] Implement generate_answer() in src/rag/generation.py (construct prompt with context chunks, call LLM, parse response for citations)
- [ ] T041 [US3] Create prompt template for answer generation (system instructions emphasizing citations and hallucination avoidance)
- [ ] T042 [US3] Implement citation parsing logic in src/rag/generation.py (extract [1], [2] references, map to chunk IDs)
- [ ] T043 [US3] Implement chat_with_documents() orchestration in src/rag/orchestration.py (coordinate search + generation)
- [ ] T044 [US3] Implement CLI chat command in src/cli/main.py (interactive REPL loop, handle exit/quit commands)
- [ ] T045 [US3] Add citation formatting in CLI output (show source filenames and chunk positions)
- [ ] T046 [US3] Handle insufficient context case (when no relevant chunks found, respond appropriately)

**Checkpoint**: All three core user stories (P1-P3) complete - Full RAG pipeline functional

---

## Phase 6: User Story 4 - Query Enhancement and Optimization (Priority: P4)

**Goal**: Vague or ambiguous queries are expanded/clarified to improve retrieval quality

**Independent Test**: Compare retrieval results before/after query expansion for ambiguous queries, verify improved relevance

### Implementation for User Story 4

- [ ] T047 [P] [US4] Implement expand_query() in src/rag/pre_retrieval.py (use Qwen3-Max to expand/rewrite query, add synonyms, expand abbreviations)
- [ ] T048 [P] [US4] Create query expansion prompt template (emphasize adding context while staying concise)
- [ ] T049 [US4] Implement preprocess_query() in src/rag/pre_retrieval.py (coordinate expansion based on enable_expansion flag)
- [ ] T050 [US4] Add query length check (only expand queries <5 words for MVP)
- [ ] T051 [US4] Integrate preprocess_query() into search_documents() orchestration in src/rag/orchestration.py
- [ ] T052 [US4] Add --expand-query CLI flag to search and chat commands in src/cli/main.py
- [ ] T053 [US4] Add logging for original vs expanded queries

**Checkpoint**: Query expansion feature complete and configurable

---

## Phase 7: User Story 5 - Result Reranking and Filtering (Priority: P5)

**Goal**: Retrieved chunks are reranked using cross-encoder for better relevance before generation

**Independent Test**: Compare answer quality with/without reranking, verify reranked results have better citation relevance

### Implementation for User Story 5

- [ ] T054 [P] [US5] Implement rerank_chunks() in src/rag/post_retrieval.py (use DashScope gte-rerank model, update similarity scores)
- [ ] T055 [US5] Add fallback logic in rerank_chunks() (return original chunks with warning if rerank API fails)
- [ ] T056 [US5] Integrate reranking into search_documents() orchestration in src/rag/orchestration.py (apply after hybrid search if enabled)
- [ ] T057 [US5] Add --no-rerank CLI flag to search and chat commands in src/cli/main.py
- [ ] T058 [US5] Add logging for rerank timing and score changes

**Checkpoint**: Reranking feature complete, can be toggled on/off

---

## Phase 8: User Story 6 - Multi-Step Reasoning and Orchestration (Priority: P6)

**Goal**: Complex multi-part queries trigger iterative retrieval-generation cycles for comprehensive answers

**Independent Test**: Submit complex multi-faceted question, verify system performs multiple retrieval rounds and synthesizes answer

### Implementation for User Story 6

- [ ] T059 [P] [US6] Implement query decomposition logic in src/rag/pre_retrieval.py (break complex query into sub-queries using LLM)
- [ ] T060 [P] [US6] Create prompt template for query decomposition (identify multiple question components)
- [ ] T061 [US6] Implement iterative_search() in src/rag/orchestration.py (perform multiple retrieval-generation cycles, accumulate context)
- [ ] T062 [US6] Implement answer synthesis logic in src/rag/generation.py (combine multiple sub-answers into coherent response)
- [ ] T063 [US6] Add multi-step reasoning flag to QueryOptions in src/models/query.py
- [ ] T064 [US6] Integrate iterative workflow into chat_with_documents() orchestration in src/rag/orchestration.py
- [ ] T065 [US6] Add logging for orchestration steps (sub-queries, iterations, synthesis)

**Checkpoint**: All six user stories complete - Advanced RAG system with orchestration

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T066 [P] Add comprehensive error messages for all CLI commands (file not found, API errors, invalid arguments)
- [ ] T067 [P] Add --verbose flag implementation across all CLI commands (enable debug logging)
- [ ] T068 [P] Create README.md with project overview, setup instructions, and usage examples
- [ ] T069 [P] Validate all type hints are complete (run mypy or equivalent)
- [ ] T070 [P] Run ruff linting and formatting across entire codebase
- [ ] T071 Add health check functionality (verify Memgraph connection, Chroma accessibility, API key validity)
- [ ] T072 Add document listing functionality (query all documents in a namespace)
- [ ] T073 [P] Unit tests for PDF parsing edge cases in tests/unit/test_parsing.py
- [ ] T074 [P] Unit tests for chunking logic in tests/unit/test_chunking.py
- [ ] T075 [P] Unit tests for embedding batching in tests/unit/test_embedding.py
- [ ] T076 Performance benchmarking script (measure indexing throughput, retrieval latency, generation time)
- [ ] T077 Run quickstart.md validation (ensure all commands work as documented)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (works with US1 data)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses retrieval from US2 but can be independent
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Pre-retrieval enhancement is independent
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Post-retrieval enhancement is independent
- **User Story 6 (P6)**: Can start after Foundational (Phase 2) - Orchestration layer is independent

**Key Insight**: All user stories are independently testable after Foundational phase. US1 must complete for data to exist, but other stories can be developed in parallel on different pipeline stages.

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services before orchestration
- Core implementation before CLI integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational model tasks (T009-T013) can run in parallel
- All Foundational storage setup tasks (T014-T015) can run in parallel
- Within each user story:
  - Contract/integration tests marked [P] can run in parallel
  - Implementation tasks marked [P] (different modules) can run in parallel
- Different user stories can be worked on in parallel by different team members after Foundational phase

---

## Parallel Example: User Story 1

```bash
# Launch tests for User Story 1 together:
Task: "Contract test for CLI indexing command in tests/contract/test_cli_indexing.py"
Task: "Integration test for end-to-end indexing flow in tests/integration/test_indexing_flow.py"

# Launch parallel implementation tasks for User Story 1:
Task: "Implement parse_pdf() function in src/rag/indexing.py"
Task: "Implement chunk_text() function in src/rag/indexing.py"
# (Then wait for both to complete before embed_chunks which depends on chunked text)
```

---

## Parallel Example: User Story 2

```bash
# Launch tests for User Story 2 together:
Task: "Contract test for CLI search command in tests/contract/test_cli_search.py"
Task: "Integration test for retrieval flow in tests/integration/test_retrieval_flow.py"

# Launch parallel retrieval implementations:
Task: "Implement vector_search() in src/rag/retrieval.py"
Task: "Implement keyword_search() in src/rag/retrieval.py"
Task: "Implement graph_search() stub in src/rag/retrieval.py"
# (All different functions, no dependencies - can be fully parallel)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T016) - CRITICAL
3. Complete Phase 3: User Story 1 (T017-T026)
4. **STOP and VALIDATE**: Test document indexing independently
5. Deploy/demo if ready

**MVP Deliverable**: CLI tool that indexes PDF documents and stores them in vector/graph databases

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Semantic search working)
4. Add User Story 3 → Test independently → Deploy/Demo (Full RAG with Q&A)
5. Add User Story 4-6 → Each adds enhancement without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Indexing)
   - Developer B: User Story 2 (Retrieval)
   - Developer C: User Story 4 (Pre-retrieval)
   - Developer D: User Story 5 (Post-retrieval)
3. Then add User Story 3 (Generation) which ties retrieval to answers
4. Finally add User Story 6 (Orchestration) on top

**Note**: US3 (Generation) should ideally come after US2 (Retrieval) since it consumes retrieval results, but can be developed in parallel using mock retrieval data.

---

## Notes

- [P] tasks = different files/modules, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable after Foundational phase
- Tests are written first (contract/integration) before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- File paths are explicit for each task (no ambiguity about where code goes)
- Constitution compliance: Type hints, docstrings, structured logging, error handling throughout

---

## Task Count Summary

- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 9 tasks (BLOCKING)
- **Phase 3 (User Story 1 - P1)**: 10 tasks (2 tests + 8 implementation)
- **Phase 4 (User Story 2 - P2)**: 10 tasks (2 tests + 8 implementation)
- **Phase 5 (User Story 3 - P3)**: 10 tasks (2 tests + 8 implementation)
- **Phase 6 (User Story 4 - P4)**: 7 tasks
- **Phase 7 (User Story 5 - P5)**: 5 tasks
- **Phase 8 (User Story 6 - P6)**: 7 tasks
- **Phase 9 (Polish)**: 12 tasks

**Total**: 77 tasks

**MVP Scope** (Minimal viable product): Phases 1-3 (26 tasks) = Document indexing system

**Semantic Search MVP**: Phases 1-4 (36 tasks) = Indexing + Retrieval

**Full RAG MVP**: Phases 1-5 (46 tasks) = Indexing + Retrieval + Generation

**Production Ready**: All phases (77 tasks) = Complete RAG system with all enhancements
