<!--
Sync Impact Report
Version: 0.0.0 → 1.0.0
Modified Principles:
- [PRINCIPLE_1_NAME] → I. Verifiable Code Quality
- [PRINCIPLE_2_NAME] → II. Test Discipline & Coverage
- [PRINCIPLE_3_NAME] → III. Consistent User Experience
- [PRINCIPLE_4_NAME] → IV. Performance & Resource Guarantees
Added Sections:
- Product Experience Standards & Accessibility Guarantees
- Delivery Workflow & Review Gates
Removed Sections:
- Placeholder for Principle 5 (requirement limited to four core areas)
Templates requiring updates:
- ✅ .specify/templates/plan-template.md (Constitution Check must enforce quality, testing, UX, and performance gates; wording already supports this.)
- ✅ .specify/templates/spec-template.md (User stories already prioritize independent testing and UX/performance outcomes.)
- ✅ .specify/templates/tasks-template.md (Task grouping by story and optional tests remain compatible with new principles.)
Follow-up TODOs:
- None
-->

# MCP Claude GPT51 Constitution

## Core Principles

### I. Verifiable Code Quality
- Every change MUST pass automated formatting, linting, and static analysis before review.
- Code reviews MUST reject diffs lacking clear purpose statements, traceable requirements, or inline justification for complex logic.
- Shared modules MUST publish usage contracts (docstrings or README snippets) that describe inputs, outputs, and failure modes.

*Rationale: Enforcing auditable quality signals keeps the codebase predictable and review-friendly as the project scales.*

### II. Test Discipline & Coverage
- Red-Green-Refactor is mandatory: authors write or update failing tests before implementing behavior.
- Minimum coverage per change: unit tests for pure logic, integration tests for boundary crossings, contract or snapshot tests for public interfaces.
- Regression suites MUST run in CI for every pull request; failures block merges without exception.

*Rationale: Repeatable tests are the only acceptable evidence that quality gates are satisfied.*

### III. Consistent User Experience
- Screens, commands, and APIs MUST reuse shared design tokens, copy blocks, and interaction patterns defined in UX guidelines.
- Accessibility is non-negotiable: provide semantic structure, keyboard support, and contrast ratios that meet WCAG 2.1 AA.
- Product copy and responses MUST be localized or parameterized so that tone, casing, and formatting remain uniform across surfaces.

*Rationale: Consistency minimizes user relearning costs and reduces support burden.*

### IV. Performance & Resource Guarantees
- Each feature spec MUST declare latency, throughput, and memory budgets; implementations cannot merge without measurements that prove compliance.
- Performance regressions over 5% relative to the previous release MUST include mitigation plans or be reverted.
- Background work, polling, and data processing MUST respect platform limits (e.g., mobile battery, server CPU quotas) with backpressure or scheduling.

*Rationale: Stable performance preserves trust and prevents surprises in production costs.*

## Product Experience Standards & Accessibility Guarantees
- UX research outputs (personas, journey maps) MUST be linked in relevant specs, and deviations require explicit approval documented in plan.md.
- Design handoffs MUST include component checklists (states, error cases, loading indicators) so implementation parity can be verified.
- Accessibility audits (manual or automated) MUST accompany releases that alter interaction surfaces, with logged defects triaged as P1 issues.

## Delivery Workflow & Review Gates
1. **Specification phase**: Each user story documents measurable UX and performance outcomes plus independent acceptance tests.
2. **Planning phase**: Constitution Check in plan.md must confirm code quality tooling, test strategy, UX alignment, and performance instrumentation before implementation begins.
3. **Implementation phase**: Tasks are grouped by user story; each task references the files it touches and includes the required tests.
4. **Review phase**: Pull requests MUST attach evidence (test outputs, profiling traces, UX screenshots) proving the four core principles were honored. Missing evidence blocks approval.
5. **Post-merge verification**: Monitoring dashboards and observability hooks MUST be updated within the same release cycle to reflect new performance or UX guarantees.

## Governance
- This constitution supersedes conflicting process documents. Exceptions require written approval from the technical lead and UX lead, plus a remediation timeline.
- Amendments follow semantic versioning. MINOR bumps add or expand principles/sections. PATCH bumps clarify wording without changing obligations. MAJOR bumps retire or replace principles.
- Ratification requires consensus between engineering, QA, and UX representatives. Records of the vote, rationale, and supporting evidence MUST be stored alongside this file.
- Compliance reviews occur each release. Any violation triggers an incident report detailing the breach, user impact, and corrective actions before new work starts.
- Runtime guidance (specs, plans, tasks, README) MUST be updated or cross-checked whenever this document changes; discrepancies block release sign-off.

**Version**: 1.0.0 | **Ratified**: 2025-11-25 | **Last Amended**: 2025-11-25
