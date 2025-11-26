# Tasks: New Hire Onboarding Multi-Agent Backend

**Input**: Design documents from `/specs/001-onboarding-agents/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize repository structure, dependency management, and environment scaffolding.

- [X] T001 Create runtime directories (`app/`, `tests/`, `scripts/`, `data/`, `logs/`, `configs/`) per plan structure. (repo root)
- [X] T002 Initialize uv project environment and add baseline dependencies (LangChain, LangGraph, DeepAgents, SQLModel, Typer) in `pyproject.toml`.
- [X] T003 [P] Configure linting/formatting (Ruff + Black) and pre-commit hooks in `.ruff.toml`, `pyproject.toml`, and `.pre-commit-config.yaml`.
- [ ] T004 [P] Create `.env.example` with placeholders (Qwen, LangSmith, MCP) and add loader stub in `app/config.py`.
- [ ] T005 Scaffold `scripts/verify_env.py` to assert required environment keys exist before runtime.
- [ ] T006 Document local bootstrap instructions in `README.md` referencing `quickstart.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required by all user stories.

- [ ] T007 Implement global settings loader and SecretStr masking in `app/config.py`.
- [ ] T008 Define SQLModel base (`app/models/base.py`) and initialize SQLite engine/session factory in `app/services/db.py`.
- [ ] T009 [P] Create shared telemetry utilities with timing/log masking in `app/telemetry/metrics.py`.
- [ ] T010 Seed bilingual role asset JSON and loader CLI (`scripts/seed_role_assets.py` + `data/role_assets.json`).
- [ ] T011 [P] Implement MCP client wrapper with retry/backoff in `app/integrations/mcp_client.py`.
- [ ] T012 [P] Implement Qwen text + VL client utilities in `app/integrations/qwen_client.py`.
- [ ] T013 Define domain entities per data model in `app/models/` (session, profile, checklist_item, role_asset, provisioning_request, qa_log).
- [ ] T014 Establish LangGraph state container and base workflow entry (`app/workflows/onboarding_graph.py`).
- [ ] T015 Create Typer CLI entry (`main.py`) to launch chat workflow with LangGraph runner.
- [ ] T016 Setup tests scaffolding (`tests/unit/conftest.py`, `tests/contract/conftest.py`, `tests/integration/conftest.py`) including SQLite in-memory fixtures and mock MCP servers.
- [ ] T017 Add logging configuration (structured JSON) in `app/config/logging.py` referenced across agents.
- [ ] T018 Create shared copy catalog for bilingual strings in `app/copy/catalog.py`.
- [ ] T019 Establish persistent checklist service skeleton in `app/services/checklist.py` with CRUD stubs.
- [ ] T020 Configure CI script (GitHub workflow or local script) to run lint, unit, contract, and integration suites as per constitution (`.github/workflows/ci.yml`).

**Checkpoint**: All infrastructure ready; user stories can proceed.

---

## Phase 3: User Story 1 – Guided onboarding kickoff (Priority: P1) 🎯 MVP

**Goal**: Supervisor agent greets new hires, presents onboarding overview, and maintains a live checklist accessible on demand.
**Independent Test**: Start a new session via CLI, confirm checklist creation, supervisor summary, and status query response without completing later steps.

### Tests (write first)
- [ ] T021 [P] [US1] Create integration test `tests/integration/test_us1_supervisor.py` simulating kickoff/checklist query via LangGraph harness.
- [ ] T022 [P] [US1] Add unit tests for checklist state machine transitions in `tests/unit/test_checklist.py`.

### Implementation
- [ ] T023 [P] [US1] Implement checklist persistence logic (create/update/query) in `app/services/checklist.py`.
- [ ] T024 [P] [US1] Build supervisor agent node handling greetings and checklist rendering in `app/agents/supervisor.py`.
- [ ] T025 [US1] Connect supervisor node into `app/workflows/onboarding_graph.py` initial branch and register event hooks.
- [ ] T026 [US1] Extend Typer CLI prompts in `main.py` to capture employee ID + language and start LangGraph session.
- [ ] T027 [US1] Implement checklist status command handler to allow employee status queries (supervisor agent + CLI binding).
- [ ] T028 [US1] Add structured logging + telemetry spans for supervisor actions in `app/telemetry/metrics.py`.
- [ ] T029 [US1] Update documentation (`quickstart.md`) with instructions for verifying kickoff flow.

**Checkpoint**: MVP deliverable—new hire sees intro and checklist; tests green.

---

## Phase 4: User Story 2 – Identity verification and correction (Priority: P2)

**Goal**: Identity agent guides ID upload, validates via Qwen VL, extracts legal data, and loops until success.
**Independent Test**: Provide mock image payloads; confirm rejection feedback and success path storing profile data without touching later stories.

### Tests
- [ ] T030 [P] [US2] Add contract test for `/onboarding/sessions/{id}/identity` request schema in `tests/contract/test_identity_endpoint.py`.
- [ ] T031 [P] [US2] Extend integration script `tests/integration/fixtures/onboarding_happy_path.jsonl` with identity scenarios and assert outcomes in `tests/integration/test_us2_identity.py`.

### Implementation
- [ ] T032 [P] [US2] Implement identity validation service calling Qwen VL in `app/services/identity_validation.py` with error taxonomy.
- [ ] T033 [P] [US2] Add storage handlers for temporary image metadata and cleanup in `app/services/storage.py`.
- [ ] T034 [US2] Build identity agent node in `app/agents/identity.py` handling upload prompts, validation results, and retry guidance.
- [ ] T035 [US2] Wire identity node after supervisor step in `app/workflows/onboarding_graph.py`, updating session status transitions.
- [ ] T036 [US2] Persist extracted legal fields into `app/models/employee_profile.py` via service layer.
- [ ] T037 [US2] Implement API handler for `/onboarding/sessions/{sessionId}/identity` defined in `app/workflows/onboarding_graph.py`/`app/routers/onboarding.py` (create router if needed).
- [ ] T038 [US2] Enhance logging for identity failures with PII-safe masking in `app/telemetry/metrics.py`.
- [ ] T039 [US2] Update `quickstart.md` troubleshooting with identity upload guidance.

**Checkpoint**: Identity flow independently testable.

---

## Phase 5: User Story 3 – Profile data collection and role briefing (Priority: P3)

**Goal**: Collect school/degree/role, validate inputs, and deliver tailored role responsibilities via knowledge agent.
**Independent Test**: Provide valid/invalid inputs via CLI; confirm validation feedback and responsibility summary without provisioning accounts.

### Tests
- [ ] T040 [P] [US3] Unit tests for profile validators (`tests/unit/test_profile_validation.py`).
- [ ] T041 [P] [US3] Contract test for `/onboarding/sessions/{id}/profile` payload in `tests/contract/test_profile_endpoint.py`.
- [ ] T042 [US3] Integration test covering profile submission + role brief retrieval in `tests/integration/test_us3_profile.py`.

### Implementation
- [ ] T043 [P] [US3] Implement profile form agent prompts + validation messaging in `app/agents/profile.py`.
- [ ] T044 [P] [US3] Add role knowledge lookup service referencing role assets in `app/services/role_briefing.py`.
- [ ] T045 [US3] Build responsibilities delivery agent (`app/agents/qa.py` or dedicated `role_brief_agent.py`) to send summary and post-task list.
- [ ] T046 [US3] Store validation results + role brief reference on `EmployeeProfile` (update `app/models/employee_profile.py`).
- [ ] T047 [US3] Implement `/onboarding/sessions/{sessionId}/responsibilities` handler aligning to contract in `app/routers/onboarding.py`.
- [ ] T048 [US3] Update LangGraph workflow to trigger knowledge agent after profile completion.
- [ ] T049 [US3] Extend CLI prompts to show summarized responsibilities and capture acknowledgement.

**Checkpoint**: Profile + briefing flow fully testable.

---

## Phase 6: User Story 4 – Access provisioning and wrap-up (Priority: P4)

**Goal**: Provision role-specific accounts via MCP tools, return credentials, and deliver offline reminder checklist.
**Independent Test**: Run provisioning with mock MCP servers to confirm correct tool selection, credential return, and final reminders.

### Tests
- [ ] T050 [P] [US4] Contract tests for provisioning endpoint `/onboarding/sessions/{id}/provisioning` in `tests/contract/test_provisioning_endpoint.py`.
- [ ] T051 [US4] Integration test covering tooling agent + reminder summary in `tests/integration/test_us4_provisioning.py` using mock MCP responses.

### Implementation
- [ ] T052 [P] [US4] Implement provisioning decision matrix (role → tool) in `app/services/provisioning.py`.
- [ ] T053 [P] [US4] Build tooling agent node (`app/agents/tooling.py`) to call MCP client and handle retries/escalations.
- [ ] T054 [US4] Persist provisioning results + credential references in `app/models/account_provisioning_request.py`.
- [ ] T055 [US4] Implement secure credential presentation flow (mask + acknowledgement) in supervisor agent update (`app/agents/supervisor.py`).
- [ ] T056 [US4] Add offline reminder generator referencing copy catalog in `app/agents/supervisor.py` / `app/copy/catalog.py`.
- [ ] T057 [US4] Expose `/onboarding/sessions/{sessionId}/status` API updates to include credential confirmation and reminders in `app/routers/onboarding.py`.
- [ ] T058 [US4] Update telemetry to capture provisioning latency + success metrics in `app/telemetry/metrics.py`.

**Checkpoint**: Digital onboarding completed with provisioning + reminders.

---

## Phase 7: Polish & Cross-Cutting

**Purpose**: Final quality improvements, documentation, and test execution.

- [ ] T059 [P] Add multilingual copy review + UX consistency check to `docs/UX/onboarding_copy.md`.
- [ ] T060 Harden security: ensure PII encryption at rest and redact logs (`app/services/security.py`).
- [ ] T061 [P] Optimize LangGraph performance (concurrency limits, caching) documented in `app/workflows/onboarding_graph.py` comments.
- [ ] T062 Run full test matrix (`uv run pytest tests`) and capture artifacts in `docs/testing/onboarding_report.md`.
- [ ] T063 Address any failing integration tests by updating responsible modules and documenting fixes in commit notes.
- [ ] T064 Update `README.md` and `quickstart.md` with final instructions + troubleshooting matrix.

---

## Dependencies & Execution Order

1. **Phase 1 → Phase 2**: Setup must finish before foundational work; no user story may start earlier.
2. **Phase 2 → Phases 3-6**: Foundational infrastructure (DB, agents, MCP clients) is prerequisite for all user stories.
3. **User Stories**: Execute in priority order (US1 → US2 → US3 → US4). Later stories depend on data captured in earlier ones but remain independently testable once prerequisites satisfied.
4. **Phase 7**: Polish tasks require all targeted user stories to be complete.

### Parallel Opportunities
- Tasks marked [P] operate on separate files (e.g., integrations vs services) and can run concurrently within a phase.
- After Phase 2, different teams can handle US2–US4 in parallel provided shared entities are stable.
- Test authoring tasks (e.g., T021, T030, T040, T050) can run simultaneously while implementation progresses, as long as red-green discipline is maintained.

## Implementation Strategy

1. **MVP Scope**: Complete Phases 1–3 (Setup, Foundation, User Story 1). This delivers a guided onboarding kickoff with checklist visibility.
2. **Incremental Delivery**:
   - Sprint 1: MVP (US1) validated via integration/regression tests.
   - Sprint 2: Add identity verification (US2) and re-run full suite.
   - Sprint 3: Layer profile + role briefing (US3).
   - Sprint 4: Finish provisioning + wrap-up (US4) and polish tasks.
3. **Testing Discipline**: For each story, write tests first (per tasks) to enforce red-green-refactor cycle. Continuous integration (T020) must run lint + all pytest suites on every push.

## Summary Metrics
- **Total Tasks**: 64
- **Per User Story**:
  - US1: 9 tasks
  - US2: 10 tasks
  - US3: 10 tasks
  - US4: 9 tasks
- **Parallel Opportunities**: 18 tasks flagged [P]; additional concurrency possible across independent stories after Phase 2.
- **Independent Tests**: Each story includes dedicated integration/unit/contract coverage ensuring isolated verification.
- **MVP Recommendation**: Deliver through US1 before expanding to identity/profile/provisioning flows.
