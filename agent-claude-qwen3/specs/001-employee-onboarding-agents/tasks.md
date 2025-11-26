# Tasks: Employee Onboarding Multi-Agent Backend System

**Input**: Design documents from `/specs/001-employee-onboarding-agents/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks as part of the comprehensive testing approach outlined in the specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with deepagents and langchain dependencies
- [ ] T003 [P] Configure linting and formatting tools (ruff, black)
- [ ] T004 [P] Set up pytest configuration and test directory structure
- [ ] T005 Create .env file with configuration variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Setup database schema and migrations framework (SQLite for dev, PostgreSQL for prod)
- [ ] T007 [P] Implement database connection and session management in src/utils/database.py
- [ ] T008 [P] Setup configuration management with python-dotenv in src/utils/config.py
- [ ] T009 [P] Create base model classes in src/models/__init__.py
- [ ] T010 Create error handling and logging infrastructure in src/utils/exceptions.py
- [ ] T011 Setup MCP client base class in src/services/mcp_client.py
- [ ] T012 Configure Qwen API client in src/services/qwen_client.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Complete Onboarding Process (Priority: P1) 🎯 MVP

**Goal**: Enable new employees to go through the complete onboarding process including ID verification, information collection, responsibility announcement, permission granting, and post-onboarding task reminders.

**Independent Test**: Can be fully tested by initiating the onboarding process and verifying successful completion of all steps including ID verification, information collection, responsibility announcement, permission granting, and post-onboarding task reminders.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Contract test for session creation endpoint in tests/contract/test_session.py
- [ ] T014 [P] [US1] Contract test for ID photo upload endpoint in tests/contract/test_id_upload.py
- [ ] T015 [P] [US1] Contract test for information collection endpoint in tests/contract/test_information.py
- [ ] T016 [P] [US1] Integration test for complete onboarding flow in tests/integration/test_complete_onboarding.py

### Implementation for User Story 1

- [ ] T017 [P] [US1] Create Employee model in src/models/employee.py
- [ ] T018 [P] [US1] Create OnboardingChecklist model in src/models/onboarding_checklist.py
- [ ] T019 [P] [US1] Create IDPhoto model in src/models/id_photo.py
- [ ] T020 [P] [US1] Create AccountCredentials model in src/models/credentials.py
- [ ] T021 [P] [US1] Create enums in src/models/__init__.py (EducationLevel, OnboardingStatus, VerificationStatus)
- [ ] T022 [US1] Implement database repository layer in src/repositories/employee_repository.py
- [ ] T023 [US1] Implement ID verification service in src/services/id_verification_service.py
- [ ] T024 [US1] Implement position service in src/services/position_service.py
- [ ] T025 [US1] Implement supervisor agent in src/agents/supervisor.py
- [ ] T026 [US1] Implement identity verification agent in src/agents/identity_verification.py
- [ ] T027 [US1] Implement information collection agent in src/agents/information_collection.py
- [ ] T028 [US1] Implement session management in src/services/session_service.py
- [ ] T029 [US1] Create API endpoints for session creation in src/api/sessions.py
- [ ] T030 [US1] Create API endpoints for ID photo upload in src/api/id_photo.py
- [ ] T031 [US1] Create API endpoints for information collection in src/api/information.py
- [ ] T032 [US1] Implement API router and server setup in src/api/__init__.py
- [ ] T033 [US1] Add validation and error handling for all endpoints
- [ ] T034 [US1] Add logging for onboarding operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Handle Invalid ID Photo Submission (Priority: P2)

**Goal**: Provide clear feedback when ID photo submissions are invalid so users can correct and resubmit successfully.

**Independent Test**: Can be tested by submitting invalid ID photos and verifying the system provides clear corrective guidance.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T035 [P] [US2] Contract test for invalid ID photo submission in tests/contract/test_invalid_id.py
- [ ] T036 [P] [US2] Integration test for error handling flow in tests/integration/test_id_errors.py

### Implementation for User Story 2

- [ ] T037 [P] [US2] Enhance ID verification service with quality checks in src/services/id_verification_service.py
- [ ] T038 [P] [US2] Add document type validation in src/services/id_verification_service.py
- [ ] T039 [US2] Implement error feedback mechanism in src/agents/identity_verification.py
- [ ] T040 [US2] Create API endpoint for ID verification status in src/api/id_photo.py
- [ ] T041 [US2] Add validation rules and error messages in src/utils/validators.py
- [ ] T042 [US2] Update IDPhoto model with enhanced error tracking in src/models/id_photo.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Get Answers to Onboarding Questions (Priority: P3)

**Goal**: Allow employees to ask questions about the onboarding process and receive clear answers.

**Independent Test**: Can be tested by asking various onboarding-related questions and verifying the system provides accurate, helpful responses.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T043 [P] [US3] Contract test for question answering endpoint in tests/contract/test_qa.py
- [ ] T044 [P] [US3] Integration test for Q&A flow in tests/integration/test_qa.py

### Implementation for User Story 3

- [ ] T045 [P] [US3] Implement Q&A service in src/services/qa_service.py
- [ ] T046 [P] [US3] Create knowledge base management in src/services/knowledge_base.py
- [ ] T047 [US3] Implement Q&A agent in src/agents/qa.py
- [ ] T048 [US3] Create API endpoint for question answering in src/api/qa.py
- [ ] T049 [US3] Add position responsibilities data management in src/services/position_service.py
- [ ] T050 [US3] Implement post-onboarding tasks service in src/services/post_tasks_service.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Tool Calling Agent Implementation

**Goal**: Implement the tool calling agent to handle MCP integrations for account provisioning.

**Independent Test**: Can be tested by simulating account provisioning requests and verifying the system correctly calls MCP tools.

### Tests for Tool Calling Agent (OPTIONAL - only if tests requested) ⚠️

- [ ] T051 [P] Contract test for account provisioning endpoint in tests/contract/test_provisioning.py
- [ ] T052 [P] Integration test for MCP tool calling in tests/integration/test_mcp_integration.py

### Implementation for Tool Calling Agent

- [ ] T053 [P] Enhance MCP client with account provisioning methods in src/services/mcp_client.py
- [ ] T054 [P] Create account provisioning service in src/services/account_provisioning_service.py
- [ ] T055 Implement tool calling agent in src/agents/tool_calling.py
- [ ] T056 Create API endpoints for account provisioning in src/api/provisioning.py
- [ ] T057 Add account provisioning to supervisor agent workflow in src/agents/supervisor.py

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T058 [P] Documentation updates in docs/
- [ ] T059 Code cleanup and refactoring across all modules
- [ ] T060 Performance optimization across all stories
- [ ] T061 [P] Additional unit tests in tests/unit/
- [ ] T062 Security hardening for API endpoints
- [ ] T063 Run quickstart.md validation
- [ ] T064 Add comprehensive logging and monitoring
- [ ] T065 Implement caching for position responsibilities
- [ ] T066 Add rate limiting for API endpoints
- [ ] T067 Create deployment scripts and configuration

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
Task: "Contract test for session creation endpoint in tests/contract/test_session.py"
Task: "Contract test for ID photo upload endpoint in tests/contract/test_id_upload.py"
Task: "Contract test for information collection endpoint in tests/contract/test_information.py"
Task: "Integration test for complete onboarding flow in tests/integration/test_complete_onboarding.py"

# Launch all models for User Story 1 together:
Task: "Create Employee model in src/models/employee.py"
Task: "Create OnboardingChecklist model in src/models/onboarding_checklist.py"
Task: "Create IDPhoto model in src/models/id_photo.py"
Task: "Create AccountCredentials model in src/models/credentials.py"
Task: "Create enums in src/models/__init__.py (EducationLevel, OnboardingStatus, VerificationStatus)"
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

All tasks MUST adhere to the project constitution principles:

### Code Quality Standards

- All code changes MUST follow consistent naming conventions
- Public APIs MUST be documented before merging
- Code reviews MUST verify maintainability and clarity

### Testing Excellence

- Unit tests MUST cover core business logic with target coverage
- Integration tests MUST validate external service interactions
- End-to-end tests MUST verify critical user journeys

### User Experience Consistency

- All UI changes MUST maintain unified design language
- Terminology MUST be consistent across all user-facing elements
- Accessibility guidelines MUST be followed in all implementations

### Performance Optimization

- Performance targets MUST be defined and measured
- Resource utilization MUST be optimized per constitution requirements
- Monitoring MUST be implemented for all new features