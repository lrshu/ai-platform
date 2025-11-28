# Tasks: RAG Backend System

**Input**: Design documents from `/specs/001-rag-backend/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with LangChain dependencies in pyproject.toml
- [ ] T003 [P] Configure linting and formatting tools (ruff, black) in pyproject.toml
- [ ] T004 [P] Create .env file with required configuration variables
- [ ] T005 [P] Set up pytest configuration in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Setup Memgraph database connection in src/lib/database.py
- [ ] T007 [P] Implement configuration management in src/lib/config.py
- [ ] T008 [P] Setup logging infrastructure in src/lib/logging.py
- [ ] T009 [P] Implement error handling framework in src/lib/exceptions.py
- [ ] T010 Create base model classes in src/models/base.py
- [ ] T011 Setup Qwen API client in src/lib/llm_client.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Document Indexing Pipeline (Priority: P1) 🎯 MVP

**Goal**: Enable system administrators to index PDF documents into the RAG system for later search and retrieval

**Independent Test**: Upload a PDF document and verify that it gets parsed, chunked, vectorized, and stored in the database with its knowledge graph representation

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Integration test for PDF parsing in tests/integration/test_indexing.py
- [ ] T013 [P] [US1] Unit test for document chunking in tests/unit/test_chunker.py
- [ ] T014 [P] [US1] Unit test for vector generation in tests/unit/test_vector_store.py

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create Document model in src/models/document.py
- [ ] T016 [P] [US1] Create Chunk model in src/models/chunk.py
- [ ] T017 [P] [US1] Create Vector model in src/models/vector.py
- [ ] T018 [P] [US1] Create KnowledgeGraph model in src/models/knowledge_graph.py
- [ ] T019 [P] [US1] Implement PDF parser in src/lib/pdf_parser.py
- [ ] T020 [P] [US1] Implement document chunker in src/lib/chunker.py
- [ ] T021 [P] [US1] Implement vector store in src/lib/vector_store.py
- [ ] T022 [P] [US1] Implement graph store in src/lib/graph_store.py
- [ ] T023 [US1] Implement indexing service in src/services/indexing.py (depends on T019, T020, T021, T022)
- [ ] T024 [US1] Add validation for PDF files and error handling in indexing service
- [ ] T025 [US1] Add logging for indexing operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Document Retrieval and Search (Priority: P2)

**Goal**: Enable end users to search for information in indexed documents and retrieve relevant content

**Independent Test**: Ask a question about previously indexed content and verify that relevant document chunks are retrieved and ranked appropriately

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T026 [P] [US2] Integration test for search functionality in tests/integration/test_retrieval.py
- [ ] T027 [P] [US2] Unit test for query expansion in tests/unit/test_pre_retrieval.py

### Implementation for User Story 2

- [ ] T028 [P] [US2] Create Query model in src/models/query.py
- [ ] T029 [P] [US2] Create SearchResult model in src/models/search_result.py
- [ ] T030 [P] [US2] Implement pre-retrieval service in src/services/pre_retrieval.py
- [ ] T031 [P] [US2] Implement retrieval service in src/services/retrieval.py
- [ ] T032 [P] [US2] Implement post-retrieval service in src/services/post_retrieval.py
- [ ] T033 [US2] Add hybrid search combining vector and graph search in retrieval service
- [ ] T034 [US2] Add result reranking using DashScopeRerank
- [ ] T035 [US2] Add validation and error handling for search operations
- [ ] T036 [US2] Add logging for search operations

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Conversational Question Answering (Priority: P3)

**Goal**: Enable end users to have conversations with the system about indexed documents and receive comprehensive answers

**Independent Test**: Engage in a conversation with the system about indexed content and verify that responses are coherent and based on the document content

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T037 [P] [US3] Integration test for chat functionality in tests/integration/test_generation.py
- [ ] T038 [P] [US3] Unit test for prompt assembly in tests/unit/test_generation.py

### Implementation for User Story 3

- [ ] T039 [P] [US3] Create Conversation model in src/models/conversation.py
- [ ] T040 [P] [US3] Create Response model in src/models/response.py
- [ ] T041 [P] [US3] Implement generation service in src/services/generation.py
- [ ] T042 [P] [US3] Implement orchestration service in src/services/orchestration.py
- [ ] T043 [US3] Add conversation context management in orchestration service
- [ ] T044 [US3] Add validation and error handling for chat operations
- [ ] T045 [US3] Add logging for chat operations

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: CLI Interface Implementation

**Purpose**: Implement the command-line interface for all user stories

- [ ] T046 Implement main CLI entry point in src/cli/main.py
- [ ] T047 [P] Add indexing command with --name and --file parameters
- [ ] T048 [P] Add search command with --name and --question parameters
- [ ] T049 [P] Add chat command with --name parameter
- [ ] T050 [P] Add global options (--top_k, --expand-query, --rerank, etc.)
- [ ] T051 Add help documentation for all commands
- [ ] T052 Add validation for command-line arguments
- [ ] T053 Add error handling for CLI operations

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T054 [P] Add comprehensive unit tests for all components in tests/unit/
- [ ] T055 [P] Add integration tests for complete workflows in tests/integration/
- [ ] T056 [P] Add contract tests for CLI interface in tests/contract/
- [ ] T057 Add performance optimization for large document processing
- [ ] T058 Add security hardening for API keys and database connections
- [ ] T059 Add documentation for all public interfaces
- [ ] T060 Run quickstart.md validation and update if needed
- [ ] T061 Add type hints throughout the codebase for better code quality
- [ ] T062 Add comprehensive logging for debugging and monitoring
- [ ] T063 Run all tests and ensure they pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **CLI Interface (Phase 6)**: Can proceed in parallel with user story implementation
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Integration test for PDF parsing in tests/integration/test_indexing.py"
Task: "Unit test for document chunking in tests/unit/test_chunker.py"
Task: "Unit test for vector generation in tests/unit/test_vector_store.py"

# Launch all models for User Story 1 together:
Task: "Create Document model in src/models/document.py"
Task: "Create Chunk model in src/models/chunk.py"
Task: "Create Vector model in src/models/vector.py"
Task: "Create KnowledgeGraph model in src/models/knowledge_graph.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
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

## Constitution Compliance

All task implementations MUST comply with the RAG Platform Constitution:
- **Code Quality Standards**: Code review tasks MUST be included for all new features
- **Testing Requirements**: Test tasks MUST cover at least 80% of code paths for new features
- **UX Consistency**: UI tasks MUST reference the unified design system
- **Performance Requirements**: Critical path tasks MUST include performance benchmarks