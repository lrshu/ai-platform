# Implementation Plan: New Hire Onboarding Multi-Agent Backend

**Branch**: `001-onboarding-agents` | **Date**: 2025-11-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-onboarding-agents/spec.md`

## Summary

Build a LangChain DeepAgents-based backend that orchestrates five specialized agents (supervisor, identity, profile, tooling, Q&A) to guide new hires through identity verification, profile completion, role briefing, access provisioning, and reminder delivery. The implementation will provide environment configuration, persistent onboarding session storage, MCP tooling integration for email/Git account provisioning, integration tests that simulate the full onboarding flow, and automated remediation of issues surfaced by those tests.

## Technical Context

**Language/Version**: Python 3.12 (uv-managed environment)
**Primary Dependencies**: LangChain DeepAgents, LangGraph, Qwen SDK (qwen3-max + qwen3-vl-max), MCP client SDK, Pydantic/SQLModel for data modeling, Typer CLI for `python main.py chat`
**Storage**: SQLite (via SQLModel) for onboarding sessions, checklist states, and tool results (encrypted fields for sensitive identity data)
**Testing**: Pytest with LangChain testing utilities + integration suite invoking the chat workflow through the LangGraph entry point (red-green enforced)
**Target Platform**: Cross-platform CLI/back-end process (macOS + Linux servers) reachable via `python main.py chat`
**Project Type**: Single backend service with agent orchestration and CLI entrypoint
**Performance Goals**: Sustain <10s agent turnaround per step and complete 95% of onboarding journeys inside 20 minutes; MCP provisioning latency <5s per tool call; storage ops <50ms per transaction
**Constraints**: Secure ID image lifecycle (temp storage + auto purge), rate-limited MCP calls, PII-safe telemetry masking, resumable sessions on reconnect
**Scale/Scope**: Up to 100 concurrent sessions, ~500 daily hires, full transcripts retained for compliance

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Plan Compliance | Status |
|-----------|-----------------|--------|
| Verifiable Code Quality | Enforce Ruff + Black pre-commit, document shared services via README snippets, ensure agent modules expose typed interfaces | ✅ Pass |
| Test Discipline & Coverage | Adopt red-green workflow, add unit tests for checklist/validation, contract tests for MCP payloads, integration flow test covering entire LangGraph | ✅ Pass |
| Consistent User Experience | Centralize bilingual copy in `copy/catalog.py`, reuse checklist tone/casing, align reminders with UX writing guidelines | ✅ Pass |
| Performance & Resource Guarantees | Instrument LangGraph nodes for latency metrics, cap concurrent sessions, assert provisioning latency and total journey duration in tests | ✅ Pass |

## Project Structure

### Documentation (this feature)

```text
specs/001-onboarding-agents/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md   # created later by /speckit.tasks
```

### Source Code (repository root)

```text
app/
├── config.py
├── agents/
│   ├── supervisor.py
│   ├── identity.py
│   ├── profile.py
│   ├── tooling.py
│   └── qa.py
├── services/
│   ├── checklist.py
│   ├── identity_validation.py
│   ├── role_briefing.py
│   └── provisioning.py
├── integrations/
│   ├── mcp_client.py
│   └── qwen_client.py
├── workflows/
│   └── onboarding_graph.py
└── telemetry/
    └── metrics.py

scripts/
├── seed_role_assets.py
└── verify_env.py

tests/
├── unit/
│   ├── test_checklist.py
│   └── test_identity_validation.py
├── contract/
│   └── test_mcp_payloads.py
└── integration/
    └── test_onboarding_flow.py

main.py  # Typer CLI entry, launches LangGraph workflow
```

**Structure Decision**: Single backend project rooted under `app/` keeps agents, services, integrations, and telemetry together while `tests/` mirrors runtime layers (unit/contract/integration). `scripts/` now includes both seeding and env verification utilities required by the plan.

## Phase 0 Research Summary

See `research.md` for recorded decisions on VL identity validation, storage, orchestration, MCP strategy, testing approach, and env management. All NEEDS CLARIFICATION items resolved; no outstanding blockers.

## Phase 1 Outputs

- `data-model.md`: Captures entities (OnboardingSession, EmployeeProfile, ChecklistItem, RoleKnowledgeAsset, AccountProvisioningRequest, QAInteractionLog) and state machine.
- `contracts/onboarding-api.yaml`: OpenAPI 3.1 contract covering session lifecycle, profile submission, responsibilities, provisioning, and status endpoints.
- `quickstart.md`: Setup, env configuration, testing commands, and troubleshooting tips.
- `CLAUDE.md`: Updated via agent context script to include new technologies.

## Complexity Tracking

_No constitution violations identified; no additional complexity justifications required._
