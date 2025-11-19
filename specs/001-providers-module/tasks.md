# Tasks: Providers Module (External Capabilities)

**Input**: Design documents from `/specs/001-providers-module/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Documentation First**: As per the project constitution, core functions MUST include Google-style docstrings with comprehensive type hints BEFORE implementation. Each task that involves code creation MUST include documentation as part of the implementation.

**Bilingual Documentation**: As per the project constitution, all documentation MUST be provided in both Chinese and English. Tasks that involve creating documentation files MUST create both **.md (Chinese) and **.en.md (English) versions.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Initialization & Infrastructure

**Purpose**: Project initialization and basic structure

- [ ] T001 Install uv package manager and verify Python 3.12+ environment
- [ ] T002 Create project structure according to plan.md with backend/ directory and subdirectories
- [ ] T003 [P] Initialize pyproject.toml with dependencies from plan.md including python-json5, requests, fastapi, pydantic
- [ ] T004 [P] Create config.json5 file with latest configuration structure from user input
- [ ] T005 [P] Create main.py entry point file
- [ ] T006 [P] Create placeholder directories for all modules (api, common, database, indexing, retrieval, post_retrieval, generation, providers, orchestration)

---

## Phase 2: Interface & Provider Implementation

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 [P] Define abstract base class IDatabase in app/common/interfaces.py
- [ ] T008 [P] Define abstract base class ITextGenerator in app/common/interfaces.py
- [ ] T009 [P] Define abstract base class IEmbedder in app/common/interfaces.py
- [ ] T010 [P] Define abstract base class IReranker in app/common/interfaces.py
- [ ] T011 [P] Define abstract base class IDocumentParser in app/common/interfaces.py
- [ ] T012 Implement QwenProvider class in app/providers/qwen_provider.py implementing ITextGenerator, IEmbedder, and IReranker interfaces
- [ ] T013 Implement MineruProvider class in app/providers/mineru_provider.py implementing IDocumentParser interface
- [ ] T014 Implement MemgraphDB class in app/database/memgraph_impl.py implementing IDatabase interface
- [ ] T015 [P] Create configuration loading mechanism in app/common/config_loader.py
- [ ] T016 [P] Implement logging utilities in app/common/utils.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Qwen Provider Integration for Text Generation and Embedding (Priority: P1) 🎯 MVP

**Goal**: Enable the system to leverage Qwen's capabilities for text generation, embedding, and reranking without exposing API integration details

**Independent Test**: Can be fully tested by invoking each of the implemented interfaces (ITextGenerator, IEmbedder, IReranker) and verifying that they correctly interact with Qwen's APIs and return expected results

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US1] Unit test for QwenProvider ITextGenerator implementation in tests/unit/test_qwen_provider_textgen.py
- [ ] T018 [P] [US1] Unit test for QwenProvider IEmbedder implementation in tests/unit/test_qwen_provider_embedder.py
- [ ] T019 [P] [US1] Unit test for QwenProvider IReranker implementation in tests/unit/test_qwen_provider_reranker.py

### Implementation for User Story 1

- [ ] T020 [P] [US1] Implement text generation functionality in QwenProvider with proper error handling
- [ ] T021 [P] [US1] Implement embedding functionality in QwenProvider with proper error handling
- [ ] T022 [P] [US1] Implement reranking functionality in QwenProvider with proper error handling
- [ ] T023 [US1] Add configuration support for QwenProvider to load API keys and endpoints from environment variables
- [ ] T024 [US1] Implement logging for all QwenProvider operations in app/providers/qwen_provider.py
- [ ] T025 [US1] Add retry logic and rate limiting handling for Qwen API calls
- [ ] T026 [US1] Implement service call logging to Memgraph for monitoring and debugging

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Document Parsing with Mineru Provider (Priority: P2)

**Goal**: Enable the system to parse documents and images using Mineru to extract text content from various file formats

**Independent Test**: Can be fully tested by submitting various document and image formats and verifying that the MineruProvider correctly extracts text content

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T027 [P] [US2] Unit test for MineruProvider IDocumentParser implementation in tests/unit/test_mineru_provider.py
- [ ] T028 [P] [US2] Integration test for document parsing with PDF files in tests/integration/test_document_parsing.py

### Implementation for User Story 2

- [ ] T029 [P] [US2] Implement document parsing functionality in MineruProvider with proper error handling
- [ ] T030 [P] [US2] Implement image parsing functionality in MineruProvider with proper error handling
- [ ] T031 [US2] Add configuration support for MineruProvider to load API keys and endpoints from environment variables
- [ ] T032 [US2] Implement logging for all MineruProvider operations in app/providers/mineru_provider.py
- [ ] T033 [US2] Add retry logic and error handling for Mineru API calls
- [ ] T034 [US2] Implement service call logging to Memgraph for monitoring and debugging

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Robust Error Handling and Isolation (Priority: P3)

**Goal**: Ensure the Providers module handles external API errors gracefully and isolates them from the core RAG logic

**Independent Test**: Can be tested by simulating various error conditions in external services and verifying that the Providers module handles them appropriately without affecting the core RAG pipeline

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T035 [P] [US3] Unit test for error handling in QwenProvider in tests/unit/test_qwen_provider_errors.py
- [ ] T036 [P] [US3] Unit test for error handling in MineruProvider in tests/unit/test_mineru_provider_errors.py
- [ ] T037 [P] [US3] Integration test for graceful degradation when external services are unavailable in tests/integration/test_error_handling.py

### Implementation for User Story 3

- [ ] T038 [P] [US3] Implement comprehensive exception classes for different error scenarios in app/common/utils.py
- [ ] T039 [P] [US3] Add timeout handling for all external API calls
- [ ] T040 [US3] Implement fallback mechanisms for when external services are temporarily unavailable
- [ ] T041 [US3] Add structured logging for all error conditions with appropriate log levels
- [ ] T042 [US3] Implement circuit breaker pattern for external service calls
- [ ] T043 [US3] Add security measures to prevent exposing sensitive information in logs

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Indexing Engine Implementation

**Goal**: Define Pydantic data models and implement indexing logic that depends on IEmbedder and IDocumentParser

- [ ] T044 [P] Define Pydantic data model Chunk in app/models/chunk.py
- [ ] T045 [P] Define Pydantic data model DocumentMetadata in app/models/document_metadata.py
- [ ] T046 [P] Define Pydantic data model SearchRequest in app/models/search_request.py with dynamic switch fields
- [ ] T047 Implement indexing logic in app/indexing/indexer.py that depends on IEmbedder and IDocumentParser
- [ ] T048 Ensure storage of traceability information during indexing process

---

## Phase 7: Retrieval Core Implementation

**Goal**: Implement HyDEGenerator and HybridRetriever components

- [ ] T049 Implement HyDEGenerator in app/retrieval/hyde_generator.py that depends on ITextGenerator and IEmbedder
- [ ] T050 Implement HybridRetriever in app/retrieval/hybrid_retriever.py that depends on IDatabase

---

## Phase 8: Post-Retrieval & Generation Implementation

**Goal**: Implement Reranker and LLMGenerator modules

- [ ] T051 Implement Reranker module in app/post_retrieval/reranker.py that depends on IReranker
- [ ] T052 Implement LLMGenerator in app/generation/llm_generator.py that depends on ITextGenerator

---

## Phase 9: Orchestration & API Implementation

**Goal**: Implement RAGPipeline and expose FastAPI interface

- [ ] T053 Implement RAGPipeline and configuration layer in app/orchestration/pipeline.py
- [ ] T054 Ensure RAGPipeline.run() method accepts SearchRequest object and orchestrates module execution based on dynamic switches
- [ ] T055 Expose FastAPI endpoints in app/api/main.py
- [ ] T056 Implement API documentation with bilingual support

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T057 [P] Documentation updates in docs/ (both .md and .en.md versions)
- [ ] T058 Code cleanup and refactoring
- [ ] T059 Performance optimization across all stories
- [ ] T060 [P] Additional unit tests in tests/unit/
- [ ] T061 Security hardening
- [ ] T062 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Initialization & Infrastructure (Phase 1)**: No dependencies - can start immediately
- **Interface & Provider Implementation (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Interface & Provider Implementation phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Interface & Provider Implementation (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Interface & Provider Implementation (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Interface & Provider Implementation (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Initialization tasks marked [P] can run in parallel
- All Interface & Provider Implementation tasks marked [P] can run in parallel (within Phase 2)
- Once Interface & Provider Implementation phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Unit test for QwenProvider ITextGenerator implementation in tests/unit/test_qwen_provider_textgen.py"
Task: "Unit test for QwenProvider IEmbedder implementation in tests/unit/test_qwen_provider_embedder.py"
Task: "Unit test for QwenProvider IReranker implementation in tests/unit/test_qwen_provider_reranker.py"

# Launch all implementation tasks for User Story 1 together:
Task: "Implement text generation functionality in QwenProvider with proper error handling"
Task: "Implement embedding functionality in QwenProvider with proper error handling"
Task: "Implement reranking functionality in QwenProvider with proper error handling"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Initialization & Infrastructure
2. Complete Phase 2: Interface & Provider Implementation (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Initialization & Infrastructure + Interface & Provider Implementation → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Initialization & Infrastructure + Interface & Provider Implementation together
2. Once Interface & Provider Implementation is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence