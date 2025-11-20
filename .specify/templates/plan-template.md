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
**Primary Dependencies**: FastAPI, Pydantic V2, Memgraph, Qwen/DashScope SDK
**Storage**: Memgraph (Graph + Vector)
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: RAG backend (follows Modular RAG paradigm)
**Performance Goals**: [NEEDS CLARIFICATION]
**Constraints**: [NEEDS CLARIFICATION]
**Scale/Scope**: [NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

For all RAG backend implementations, verify compliance with the [RAG Backend Platform Constitution](../../memory/constitution.md):

1. ✅ **Modular Architecture**: Does the design follow the six standardized pipeline stages?
2. ✅ **Provider Abstraction**: Are external services implemented as capability providers?
3. ✅ **Configuration-Driven**: Does the implementation use config.json5 for configuration?
4. ✅ **Documentation Standards**: Are Google-style Docstrings with Type Hints included?
5. ✅ **Directory Structure**: Does the implementation follow the prescribed directory structure?

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

```text
app/
├── api/                 # API Gateway & Endpoints
├── common/              # Core Infrastructure
│   ├── interfaces/      # Abstract Base Classes
│   │   ├── database.py
│   │   ├── generator.py
│   │   ├── embedder.py
│   │   ├── reranker.py
│   │   ├── parser.py
│   ├── config_loader.py
│   ├── models.py        # Shared Pydantic Models
│   ├── utils.py
├── database/            # Memgraph Implementation
├── indexing/            # Indexing Logic
├── retrieval/           # Retrieval Logic (Pre & Core)
├── post_retrieval/      # Post-Retrieval Logic
├── generation/          # Generation Logic
├── providers/           # External Service Providers
├── orchestration/       # Pipeline & Orchestrator
tests/
├── contract/
├── integration/
└── unit/
config.json5             # Main Configuration
pyproject.toml
main.py
```

**Structure Decision**: RAG backend implementation following the prescribed directory structure from the constitution.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |