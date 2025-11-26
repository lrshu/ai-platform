---

description: "Task list template for feature implementation"
---

# Tasks: MCP Account Provisioning Server

**Input**: Design documents from `/specs/001-provision-mcp-accounts/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Integration tests are REQUIRED for both MCP tools per specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish repository hygiene, dependencies, and configuration required before development.

- [X] T001 Initialize Python 3.12 uv environment and run `uv pip install` using `pyproject.toml`
- [X] T002 Add `.env.example` with `PORT`, `LOG_LEVEL`, and comments describing each variable at repo root
- [X] T003 Configure linting/type tools (ruff, pyright) in `pyproject.toml` and verify with `uv run ruff check .`
- [X] T004 Configure formatting hooks (black or ruff format) and document usage in `README.md`
- [X] T005 Create base directories `server/` and `tests/` with `__init__.py` to match plan structure

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be ready before any user story work.

- [X] T006 Implement `server/config.py` to load `.env`, validate required variables, and fail fast on missing values
- [X] T007 Implement `server/id_validator.py` with GB 11643-1999 checksum logic and reusable `ValidationError` classes
- [X] T008 Implement `server/transliteration.py` using `pypinyin` strict mode plus custom override table support
- [X] T009 Implement `server/password.py` generator enforcing 16-char, multi-class passwords via `secrets`
- [X] T010 Define shared DTOs in `server/models.py` (IdentitySubmission, ProvisioningResponse, AuditRecord) using `pydantic`
- [X] T011 Implement logging/auditing helper in `server/audit.py` to emit masked IDs and audit IDs
- [X] T012 Create FastAPI/fastapi-mcp application factory in `main.py` registering tool routers but without business logic
- [X] T013 Set up test scaffolding: `tests/integration/test_provisioning.py` file with async fixture bootstrapping the MCP server

**Checkpoint**: Foundation ready—validation, transliteration, password generation, config, and test harness exist.

## Phase 3: User Story 1 - Self-service email access (Priority: P1) 🎯 MVP

**Goal**: IT staff can submit name + national ID to provision deterministic email credentials with compliant passwords.

**Independent Test**: Through MCP client, invoke `email_account` with valid inputs and verify response matches contract; invalid IDs yield blocking errors with no credentials.

### Tests for User Story 1 (Required)

- [ ] T014 [P] [US1] Add happy-path integration test in `tests/integration/test_provisioning.py::test_email_account_success`
- [ ] T015 [P] [US1] Add invalid-ID test covering checksum failure in `tests/integration/test_provisioning.py::test_email_account_invalid_id`
- [ ] T016 [P] [US1] Add transliteration failure test using unsupported characters in `tests/integration/test_provisioning.py::test_email_account_transliteration_error`

### Implementation for User Story 1

- [ ] T017 [US1] Wire `server/tools/email_tool.py` to accept validated `IdentitySubmission` and call shared helpers
- [ ] T018 [P] [US1] Implement deterministic handle builder in `server/tools/email_tool.py` ensuring `{pinyin}@email.com`
- [ ] T019 [US1] Integrate password generator + audit logging, returning `ProvisioningResponse` from `server/tools/email_tool.py`
- [ ] T020 [P] [US1] Update `main.py` to register `email_account` MCP tool with schema defined in `contracts/mcp-tools.yaml`
- [ ] T021 [US1] Implement localized error payloads (code/message) for email tool in `server/errors.py`
- [ ] T022 [US1] Document email provisioning flow and required inputs in `README.md` onboarding section

**Checkpoint**: User Story 1 independently delivers email credentials and passes integration tests.

## Phase 4: User Story 2 - Git repository access (Priority: P2)

**Goal**: Development managers can provision Git credentials using the same identity data with deterministic handles and fresh passwords.

**Independent Test**: Invoke `git_account` via MCP client; confirm response provides `{pinyin}@git.com`, randomized password, and audit metadata. Duplicate requests maintain handle but rotate passwords.

### Tests for User Story 2 (Required)

- [ ] T023 [P] [US2] Add success test for git tool in `tests/integration/test_provisioning.py::test_git_account_success`
- [ ] T024 [P] [US2] Add duplicate-request test ensuring handle reuse but password rotation in `tests/integration/test_provisioning.py::test_git_account_dedup`
- [ ] T025 [P] [US2] Add config-error test ensuring tool fails when env missing in `tests/integration/test_provisioning.py::test_git_account_config_error`

### Implementation for User Story 2

- [ ] T026 [US2] Implement `server/tools/git_tool.py` reusing validation pipeline with git-specific domain logic
- [ ] T027 [P] [US2] Ensure password rotation semantics and metadata logging differences documented inside `git_tool.py`
- [ ] T028 [US2] Register `git_account` tool in `main.py` with output schema parity and add route-specific logging
- [ ] T029 [US2] Extend `server/errors.py` with git-specific remediation messages and ensure localization tables updated
- [ ] T030 [US2] Update ops documentation (`quickstart.md`) with git provisioning instructions and troubleshooting tips

**Checkpoint**: User Story 2 delivers Git credentials independently without regression to User Story 1.

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T031 [P] Add `.env` validation tests in `tests/integration/test_provisioning.py::test_missing_env_fails_fast`
- [ ] T032 [P] Add performance timing logs and verify metrics stay within SLAs in `server/audit.py`
- [ ] T033 Update `README.md` + `quickstart.md` with final run/test instructions and sample MCP payloads
- [ ] T034 Run full `uv run pytest --maxfail=1 --disable-warnings -q` and capture results for PR description
- [ ] T035 [P] Prepare release notes summarizing feature readiness and outstanding risks in `specs/001-provision-mcp-accounts/tasks.md` footer or project log

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)** → prerequisite for Foundational
- **Foundational (Phase 2)** → prerequisite for US1/US2
- **US1** must complete before US2 (shared helpers validated via MVP)
- **Polish** occurs after desired user stories conclude

### User Story Dependencies
- US1 (P1) has no prior story dependencies once foundational complete
- US2 (P2) depends on US1 deliverables to reuse validation + logging patterns

### Parallel Opportunities
- Tasks marked [P] operate on distinct files: tests per scenario, handle builders, documentation updates
- US1 tests (T014-T016) can be written concurrently
- US2 tests (T023-T025) can run in parallel once git tool scaffold exists
- Polish tasks T031 and T032 can run concurrently after core stories complete

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phases 1-2
2. Implement US1 tasks (T014-T022)
3. Validate email provisioning end-to-end; ship as minimal onboarding automation

### Incremental Delivery
1. Deliver MVP (US1)
2. Add US2 tasks to extend capabilities without disrupting email provisioning
3. Execute polish tasks for configs, docs, and release readiness

### Parallel Team Strategy
- Developer A: Focus on validation helpers + email tool
- Developer B: Own integration tests + git tool once foundational pieces land
- Shared responsibility for polish/documentation tasks at the end
