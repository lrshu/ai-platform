# Tasks: Standardized RAG Backend System

**Input**: Design documents from `/specs/002-rag-backend/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/

## Phase 1: Setup

- [x] T001 Create project structure in `src/` and `tests/` as defined in `plan.md`.
- [x] T002 [P] Initialize `pyproject.toml` with dependencies: `langchain`, `memgraph`, `typer`, `python-dotenv`, `pyarrow`, `pymupdf`.
- [x] T003 [P] Create `docker-compose.yml` for Memgraph.
- [x] T004 [P] Configure `pytest` in `pyproject.toml` or `pytest.ini`.

---

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T005 Implement configuration loading from `.env` in `src/rag_backend/config.py`.
- [x] T006 Implement Memgraph connection logic in `src/rag_backend/database.py`.
- [x] T007 [P] Define data models/schemas in `src/rag_backend/models.py` corresponding to `data-model.md`.
- [x] T008 Setup CLI application structure with Typer in `src/main.py`.

---

## Phase 3: User Story 1 - Document Indexing (Priority: P1) 🎯 MVP

**Goal**: Index PDF documents into a named knowledge base.
**Independent Test**: Run `python main.py indexing` with a test PDF and verify completion.

### Tests for User Story 1
- [x] T009 [P] [US1] Write unit test for PDF parsing in `tests/unit/test_indexing.py`.
- [x] T010 [P] [US1] Write unit test for text chunking in `tests/unit/test_indexing.py`.
- [ ] T011 [US1] Write integration test for the full indexing pipeline in `tests/integration/test_pipeline.py`.

### Implementation for User Story 1
- [x] T012 [P] [US1] Implement PDF parsing in `src/rag_backend/indexing.py`.
- [x] T013 [P] [US1] Implement text chunking strategy in `src/rag_backend/indexing.py`.
- [x] T014 [US1] Implement vector embedding generation for chunks in `src/rag_backend/indexing.py`.
- [x] T015 [US1] Implement knowledge graph extraction (entities, relationships) in `src/rag_backend/indexing.py`.
- [x] T016 [US1] Implement storage logic to save chunks and graph to Memgraph in `src/rag_backend/database.py`.
- [ ] T017 [US1] Implement the overall indexing pipeline in `src/rag_backend/orchestration.py`.
- [ ] T018 [US1] Add the `indexing` command to `src/main.py`.

---

## Phase 4: User Story 2 - Content Retrieval (Priority: P2)

**Goal**: Retrieve relevant document excerpts for a given question.
**Independent Test**: Run `python main.py search` and verify relevant chunks are returned.

### Tests for User Story 2
- [ ] T019 [P] [US2] Write unit test for query expansion in `tests/unit/test_pre_retrieval.py`.
- [ ] T020 [P] [US2] Write unit test for hybrid search logic in `tests/unit/test_retrieval.py`.
- [ ] T021 [US2] Write integration test for the search pipeline in `tests/integration/test_pipeline.py`.

### Implementation for User Story 2
- [ ] T022 [P] [US2] Implement query expansion in `src/rag_backend/pre_retrieval.py`.
- [ ] T023 [US2] Implement hybrid search (vector + graph) in `src/rag_backend/retrieval.py`.
- [ ] T024 [US2] Implement result re-ranking in `src/rag_backend/post_retrieval.py`.
- [ ] T025 [US2] Implement the search pipeline in `src/rag_backend/orchestration.py`.
- [ ] T026 [US2] Add the `search` command to `src/main.py`.

---

## Phase 5: User Story 3 - Conversational Answers (Priority: P3)

**Goal**: Generate a synthesized answer to a question.
**Independent Test**: Run `python main.py chat` and verify a coherent answer is returned.

### Tests for User Story 3
- [ ] T027 [P] [US3] Write unit test for prompt assembly in `tests/unit/test_generation.py`.
- [ ] T028 [US3] Write integration test for the chat pipeline in `tests/integration/test_pipeline.py`.

### Implementation for User Story 3
- [ ] T029 [P] [US3] Implement prompt assembly logic in `src/rag_backend/generation.py`.
- [ ] T030 [US3] Implement LLM call to generate answer in `src/rag_backend/generation.py`.
- [ ] T031 [US3] Implement the chat pipeline in `src/rag_backend/orchestration.py`.
- [ ] T032 [US3] Add the `chat` command to `src/main.py`.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T033 [P] Add comprehensive docstrings to all public functions and classes.
- [ ] T034 [P] Add logging to all pipeline stages.
- [ ] T035 Refine error handling and provide user-friendly error messages.
- [ ] T036 Validate and document the `quickstart.md` guide.

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** must be completed first.
- **Phase 2 (Foundational)** depends on Phase 1.
- **Phase 3 (US1)** depends on Phase 2. This is the MVP.
- **Phase 4 (US2)** depends on Phase 3.
- **Phase 5 (US3)** depends on Phase 4.
- **Phase 6 (Polish)** can be done after all user stories are complete.
