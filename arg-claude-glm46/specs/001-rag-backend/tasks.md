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
- [ ] T002 Initialize Python project with dependencies from pyproject.toml
- [ ] T003 [P] Configure linting and formatting tools (black, flake8)
- [ ] T004 [P] Set up environment variable management with python-dotenv
- [ ] T005 Create base configuration module in src/config/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Set up Memgraph database connection with neo4j driver
- [ ] T007 [P] Implement PDF parsing functionality with PyMuPDF
- [ ] T008 [P] Set up LangChain core components
- [ ] T009 [P] Configure DashScope API clients for embedding and LLM services
- [ ] T010 Create base models/entities based on data-model.md
- [ ] T011 Configure error handling and logging infrastructure
- [ ] T012 Set up environment configuration management

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Document Indexing (Priority: P1) 🎯 MVP

**Goal**: Users can add PDF documents to the system for future question answering

**Independent Test**: Can be fully tested by providing a sample PDF document and verifying that all components of the indexing pipeline execute successfully and that the processed content is stored in the database with the correct name identifier

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Contract test for indexing CLI command in tests/contract/test_indexing.py
- [ ] T014 [P] [US1] Integration test for PDF parsing in tests/integration/test_pdf_parsing.py

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create Document model in src/models/document.py
- [ ] T016 [P] [US1] Create Chunk model in src/models/chunk.py
- [ ] T017 [P] [US1] Create Entity and Relationship models in src/models/kg.py
- [ ] T018 [US1] Implement document parsing service in src/services/indexing/parser.py
- [ ] T019 [US1] Implement chunking service in src/services/indexing/chunker.py
- [ ] T020 [US1] Implement embedding generation service in src/services/indexing/embedder.py
- [ ] T021 [US1] Implement knowledge graph extraction service in src/services/indexing/kg_extractor.py
- [ ] T022 [US1] Implement storage service in src/services/indexing/storage.py
- [ ] T023 [US1] Create indexing orchestrator in src/services/indexing/orchestrator.py
- [ ] T024 [US1] Implement indexing CLI handler in src/cli/indexing.py
- [ ] T025 [US1] Add validation and error handling for file operations
- [ ] T026 [US1] Add logging for indexing operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Document Search (Priority: P1)

**Goal**: Users can search for relevant information within indexed documents by asking a question

**Independent Test**: Can be fully tested by asking a question against previously indexed documents and verifying that the system returns relevant content with appropriate ranking

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T027 [P] [US2] Contract test for search CLI command in tests/contract/test_search.py
- [ ] T028 [P] [US2] Integration test for search pipeline in tests/integration/test_search.py

### Implementation for User Story 2

- [ ] T029 [P] [US2] Create Query model in src/models/query.py
- [ ] T030 [P] [US2] Create SearchResult model in src/models/search_result.py
- [ ] T031 [US2] Implement query expansion service in src/services/pre_retrieval/query_expander.py
- [ ] T032 [US2] Implement vector search service in src/services/retrieval/vector_search.py
- [ ] T033 [US2] Implement graph search service in src/services/retrieval/graph_search.py
- [ ] T034 [US2] Implement hybrid search orchestrator in src/services/retrieval/hybrid_search.py
- [ ] T035 [US2] Implement result re-ranking service in src/services/post_retrieval/reranker.py
- [ ] T036 [US2] Create search orchestrator in src/services/retrieval/orchestrator.py
- [ ] T037 [US2] Implement search CLI handler in src/cli/search.py
- [ ] T038 [US2] Add validation and error handling for search operations
- [ ] T039 [US2] Add logging for search operations

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Conversational QA (Priority: P1)

**Goal**: Users can have conversations with the system using indexed documents as context

**Independent Test**: Can be fully tested by having a conversation with the system and verifying that answers are relevant, coherent, and based on the indexed document content

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T040 [P] [US3] Contract test for chat CLI command in tests/contract/test_chat.py
- [ ] T041 [P] [US3] Integration test for conversation flow in tests/integration/test_chat.py

### Implementation for User Story 3

- [ ] T042 [P] [US3] Create Conversation model in src/models/conversation.py
- [ ] T043 [P] [US3] Create ConversationTurn model in src/models/conversation_turn.py
- [ ] T044 [US3] Implement prompt assembly service in src/services/generation/prompt_assembler.py
- [ ] T045 [US3] Implement LLM interaction service in src/services/generation/llm_client.py
- [ ] T046 [US3] Implement answer generation service in src/services/generation/answer_generator.py
- [ ] T047 [US3] Create conversation manager in src/services/orchestration/conversation_manager.py
- [ ] T048 [US3] Implement chat CLI handler in src/cli/chat.py
- [ ] T049 [US3] Add validation and error handling for conversation operations
- [ ] T050 [US3] Add logging for conversation operations

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T051 [P] Documentation updates in README.md and docs/
- [ ] T052 Code cleanup and refactoring
- [ ] T053 Performance optimization across all stories
- [ ] T054 [P] Additional unit tests in tests/unit/
- [ ] T055 Security hardening
- [ ] T056 Run quickstart.md validation
- [ ] T057 Update main.py to integrate all CLI handlers
- [ ] T058 Add structured logging with context
- [ ] T059 Implement metrics collection for performance monitoring

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before CLI handlers
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
Task: "Contract test for indexing CLI command in tests/contract/test_indexing.py"
Task: "Integration test for PDF parsing in tests/integration/test_pdf_parsing.py"

# Launch all models for User Story 1 together:
Task: "Create Document model in src/models/document.py"
Task: "Create Chunk model in src/models/chunk.py"
Task: "Create Entity and Relationship models in src/models/kg.py"
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