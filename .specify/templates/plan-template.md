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

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the Modular RAG AI Knowledge Base Platform Constitution (v1.2.0):

1. **Pipeline Architecture Compliance**:
   - Implementation MUST follow the six-stage pipeline with specific responsibilities:
     * Indexing: Parse → Chunk → Embed → Store (Graph + Vector)
     * Pre-Retrieval: Query understanding and rewriting (HyDE, Query Expansion)
     * Retrieval: Multi-path recall (Hybrid Search)
     * Post-Retrieval: Context optimization (Rerank, Selection)
     * Generation: Prompt assembly and LLM reasoning
     * Orchestration: Dynamic module scheduling controlled by user requests
   - Direct calls to underlying logic that bypass core abstractions are PROHIBITED
   - Each stage MUST be independently testable with clear boundaries

2. **Technology Stack Compliance**:
   - Runtime: Python 3.12+ MUST be used
   - Dependency Manager: uv MUST be used
   - Web Framework: FastAPI 全异步模式 with async/await MUST be used
   - Data Validation: Pydantic V2 MUST be used
   - Database (Vector + Graph): Memgraph MUST be used
   - Model Provider (Primary): Aliyun Bailian (Qwen/DashScope) MUST be used
   - LLM Models: Qwen-Turbo/Plus/Max MUST be used
   - Embedding Model: text-embedding-v4 MUST be used
   - Rerank Model: gte-rerank MUST be used
   - Doc Parsing Provider: Mineru API MUST be used

3. **Provider Abstraction and Modular Design Compliance**:
   - External services MUST be defined as capability providers implementing specific capability interfaces
   - Capability Interfaces: ITextGenerator, IEmbedder, IReranker, IDocumentParser
   - Each pipeline stage MUST be encapsulated as an independent class following the single responsibility principle
   - Components MUST be orchestrated through a central Orchestrator
   - Direct coupling between stages is PROHIBITED

4. **Documentation First Compliance**:
   - Core functions MUST include Google-style docstrings with comprehensive type hints
   - Public APIs and service interfaces MUST be documented with clear examples

5. **Configuration Management Compliance**:
   - All configuration MUST be loaded through a config.json5 file
   - Sensitive API Keys MUST be overridden or loaded through environment variables at runtime
   - Core RAG logic MUST dynamically obtain required capability provider instances through configuration

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
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
