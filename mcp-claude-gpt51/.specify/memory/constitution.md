<!--
Sync Impact Report
Version change: (unset) → 1.0.0
Modified principles:
- NEW: I. Code Quality Gatekeeping
- NEW: II. Test Discipline Standardization
- NEW: III. Unified Experience Surfaces
- NEW: IV. Performance Budgets & Observability
- NEW: V. Continuous Verification Loop
Added sections:
- Core Principles (fully populated)
- Product Experience Guardrails
- Development Workflow & Quality Gates
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md (Constitution Check pulls mandatory gates directly from this file; no edits required)
- ✅ .specify/templates/spec-template.md (Stories + edge cases already enforce UX + performance coverage)
- ✅ .specify/templates/tasks-template.md (Phase structure supports quality/test/UX/perf traceability)
- ✅ .specify/templates/checklist-template.md (Checklist categories remain accurate for new principles)
- ✅ .specify/templates/agent-file-template.md (Summaries inherit guidance automatically)
Follow-up TODOs: None
-->

# MCP Claude GPT51 Constitution

## Core Principles

### I. Code Quality Gatekeeping
- Every change MUST pass automated formatting, linting, type checks, and static analysis. Failing checks block merge.
- Code reviews MUST confirm readability, maintainability, and removal of dead logic. Reviewers reject if intent is unclear or style deviates from documented patterns.
- Shared modules MUST expose minimal, stable interfaces; internal refactors cannot leak temporary helpers or TODO prototypes into main.
**Rationale:** Enforcing objective quality bars keeps the codebase predictable, reduces regressions, and lowers maintenance overhead.

### II. Test Discipline Standardization
- Tests MUST precede or accompany implementation (red-green-refactor). Features without automated coverage cannot ship.
- Unit, integration, and contract tests MUST declare the user story they guard so failures map directly to scope.
- Critical paths MUST reach ≥90% branch coverage; lower coverage requires a documented waiver approved in review.
**Rationale:** Consistent testing standards ensure deterministic releases and make defects observable before deployment.

### III. Unified Experience Surfaces
- UX flows MUST follow the same terminology, interaction patterns, and visual hierarchy across interfaces.
- Accessibility requirements (keyboard navigation, contrast, readable labels) are mandatory; failures block release.
- Cross-platform behavior MUST be specified in specs and validated via smoke tests before feature sign-off.
**Rationale:** Consistent experiences reduce user friction, simplify support, and reinforce trust in the product.

### IV. Performance Budgets & Observability
- Every feature MUST declare measurable latency, throughput, and resource budgets in its spec and plan.
- Baseline performance tests MUST run in CI for agreed critical scenarios; regressions >5% fail the build.
- Services MUST emit structured metrics, logs, and traces that map to declared budgets for live monitoring.
**Rationale:** Binding performance to explicit budgets prevents silent degradation and keeps capacity predictable.

### V. Continuous Verification Loop
- Each user story MUST include runnable scripts or documented commands to reproduce its quality, UX, and performance checks end-to-end.
- Plans and tasks MUST link evidence (test IDs, dashboards, screenshots) collected during implementation.
- Production incidents MUST feed back into specs and plans as new acceptance criteria before fixes merge.
**Rationale:** Closing the loop between requirements, verification, and operations hardens the system over time.

## Product Experience Guardrails

- Specs MUST define persona goals, prioritized user journeys, and failure handling that respect Principles III–V.
- Design handoffs MUST include component tokens (spacing, typography, color) and responsive states before engineering begins.
- Internationalization, localization, and accessibility concerns MUST be captured in spec edge cases to avoid retrofit work.
- Performance budgets for UX interactions (e.g., "input-to-feedback <150ms") MUST accompany each critical flow.

## Development Workflow & Quality Gates

1. **Spec Phase**: `/speckit.specify` MUST enumerate independent user stories, UX consistency checks, and performance metrics (Principles III–IV).
2. **Plan Phase**: `/speckit.plan` MUST add Constitution Check gates: quality tooling readiness, mandatory tests, UX review, and performance benchmarks.
3. **Tasks Phase**: `/speckit.tasks` MUST group work by user story, include explicit testing subtasks, and call out UX/performance verification steps.
4. **Implementation**: No code merges until automated pipelines confirm linting, tests, UX snapshots (when applicable), and performance baselines.
5. **Review & Release**: Reviewers verify evidence links (Principle V) and reject changes lacking reproducible commands or dashboards.

## Governance

- This constitution supersedes conflicting process documents. All contributors are accountable for enforcing it during planning, review, and release.
- Amendments require: (1) proposal linked to concrete pain points, (2) review by core maintainers, (3) updated version + dates recorded here, and (4) propagation across dependent templates.
- Versioning follows semantic rules: MAJOR for removals/breaking governance, MINOR for new principles/sections, PATCH for clarifications.
- Compliance audits run each release cycle; violations must be resolved or explicitly waived with rationale referenced in repo history.

**Version**: 1.0.0 | **Ratified**: 2025-11-25 | **Last Amended**: 2025-11-25
