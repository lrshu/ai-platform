# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI, Pydantic V2, uv
**Storage**: Memgraph
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: web (backend focused RAG platform)
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
backend/
├── app/
│   ├── api/                # API Gateway & Endpoints
│   ├── common/             # Core Infrastructure
│   │   ├── interfaces/     # Abstract Base Classes
│   │   │   ├── database.py
│   │   │   ├── generator.py
│   │   │   ├── embedder.py
│   │   │   ├── reranker.py
│   │   │   ├── parser.py
│   │   ├── config_loader.py
│   │   ├── models.py       # Shared Pydantic Models
│   │   ├── utils.py
│   ├── database/           # Memgraph Implementation
│   ├── indexing/           # Indexing Logic
│   ├── retrieval/          # Retrieval Logic (Pre & Core)
│   ├── post_retrieval/     # Post-Retrieval Logic
│   ├── generation/         # Generation Logic
│   ├── providers/          # External Service Providers
│   ├── orchestration/      # Pipeline & Orchestrator
├── config.json5            # Main Configuration
├── pyproject.toml
└── main.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
