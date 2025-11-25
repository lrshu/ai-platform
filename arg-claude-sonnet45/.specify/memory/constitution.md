<!--
Sync Impact Report:
Version Change: 0.0.0 → 1.0.0
Modified Principles: N/A (Initial ratification)
Added Sections:
  - Core Principles (4 principles)
  - Performance & Scalability Standards
  - Development Workflow & Quality Gates
  - Governance
Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section aligns with principles
  ✅ .specify/templates/spec-template.md - User scenarios and requirements align with UX consistency principle
  ✅ .specify/templates/tasks-template.md - Task organization supports test-first development and quality standards
Follow-up TODOs: None
-->

# arg-claude-v5 Constitution

## Core Principles

### I. Code Quality Standards (NON-NEGOTIABLE)

**Rule**: All code MUST meet the following quality standards before merge:

- **Type Safety**: Full type annotations required (Python 3.12+ type hints). No `Any` types without explicit justification.
- **Linting & Formatting**: Code MUST pass linting (ruff/pylint) and formatting (black/ruff format) checks with zero warnings.
- **Complexity Limits**: Functions > 50 lines or cyclomatic complexity > 10 require refactoring or documented justification.
- **Code Review**: All changes require peer review focusing on readability, maintainability, and adherence to principles.
- **Documentation**: Public APIs, complex logic, and non-obvious implementations MUST have clear docstrings and comments.

**Rationale**: Consistent, high-quality code reduces bugs, improves maintainability, and enables team velocity. Type safety catches errors at development time rather than production. Clear code is easier to understand, modify, and test.

### II. Test-First Development (NON-NEGOTIABLE)

**Rule**: Testing discipline is mandatory following this exact workflow:

1. **Write Tests First**: Contract and integration tests MUST be written before implementation
2. **Verify Failure**: Tests MUST fail initially (red phase)
3. **Obtain Approval**: User/stakeholder MUST approve test scenarios before implementation begins
4. **Implement**: Write minimal code to make tests pass (green phase)
5. **Refactor**: Improve code quality while keeping tests green

**Test Coverage Requirements**:
- **Contract Tests**: Required for all public APIs, CLI commands, and service boundaries
- **Integration Tests**: Required for user journeys, cross-component interactions, and data flows
- **Unit Tests**: Required for complex business logic, algorithms, and utilities
- **Minimum Coverage**: 80% line coverage, 90% for critical paths

**Rationale**: Test-first development ensures we build the right thing (tests validate requirements), prevents regression, enables confident refactoring, and serves as living documentation. Catching bugs early is 10-100x cheaper than production fixes.

### III. User Experience Consistency

**Rule**: User-facing features MUST maintain consistent experience across all touchpoints:

- **CLI Interface Standards**:
  - Consistent command structure and naming conventions
  - Clear, actionable error messages with suggested fixes
  - Progress indicators for long-running operations (>2 seconds)
  - JSON and human-readable output formats for all commands
- **API Consistency**:
  - RESTful principles for HTTP APIs
  - Consistent error response format (status code, message, details)
  - Versioned endpoints with clear deprecation policy
- **Accessibility**:
  - Clear documentation with examples for all user-facing features
  - Error messages written for non-technical users when appropriate
  - Consistent terminology throughout documentation and interfaces

**Rationale**: Consistent UX reduces cognitive load, accelerates user adoption, minimizes support overhead, and builds user trust. Users should never be surprised by inconsistent behavior or unclear messaging.

### IV. Performance & Reliability Standards

**Rule**: All features MUST meet performance targets before deployment:

- **Response Time**:
  - API endpoints: p95 < 200ms for simple queries, < 1s for complex operations
  - CLI commands: < 100ms for local operations, < 5s for remote/complex operations
  - Batch operations: Progress reporting for operations > 5 seconds
- **Resource Efficiency**:
  - Memory: No memory leaks, bounded memory growth for long-running operations
  - CPU: No blocking operations on main thread, async I/O for network/disk
  - Database: Query optimization, proper indexing, connection pooling
- **Reliability**:
  - Graceful degradation under load or partial failure
  - Proper error handling with retries for transient failures
  - Circuit breakers for external service dependencies
  - Comprehensive logging for debugging production issues

**Performance Testing Requirements**:
- Load tests for APIs handling concurrent requests
- Benchmark tests for performance-critical operations
- Memory profiling for long-running processes

**Rationale**: Poor performance and reliability destroy user trust and create support burden. Performance bugs are harder to fix later. Resource efficiency ensures scalability and cost-effectiveness.

## Performance & Scalability Standards

**Monitoring & Observability**:
- Structured logging (JSON format) for all operations
- Key metrics: request duration, error rates, resource utilization
- Distributed tracing for cross-service operations
- Health check endpoints for all services

**Scalability Requirements**:
- Stateless service design where possible
- Database queries optimized for scale (proper indexing, query analysis)
- Caching strategy for frequently accessed data
- Rate limiting for public APIs

**Constraints**: When performance targets cannot be met, document:
- Technical limitation preventing target achievement
- Measured current performance
- Mitigation plan or alternative approach
- User impact assessment

## Development Workflow & Quality Gates

**Pre-Commit Gates**:
1. All linting and formatting checks pass
2. Type checking passes with no errors
3. All tests pass (unit, integration, contract)
4. No security vulnerabilities (dependency scanning)

**Pre-Merge Gates**:
1. Code review approved by at least one team member
2. All automated tests pass in CI/CD
3. Test coverage meets minimum thresholds
4. Performance benchmarks show no regression (>10% degradation)
5. Documentation updated for API/interface changes

**Pre-Deployment Gates**:
1. Integration tests pass in staging environment
2. Load tests verify performance targets
3. Security scan shows no critical/high vulnerabilities
4. Rollback plan documented

**Branching & Commits**:
- Feature branches from main: `###-feature-name`
- Descriptive commit messages following conventional commits format
- Commits should be atomic and logically grouped
- No direct commits to main/master

**Complexity Management**:
Any violation of simplicity principles (e.g., adding frameworks, introducing abstractions, increasing dependencies) MUST be justified in writing:
- What problem it solves
- Why simpler alternatives are insufficient
- Maintenance burden assessment

## Governance

**Constitutional Authority**: This constitution supersedes all other practices, guidelines, and conventions. When in conflict, constitution takes precedence.

**Amendment Process**:
1. Proposed amendments must be documented with rationale
2. Team review and discussion period (minimum 48 hours)
3. Majority approval required
4. Version bump and migration plan required
5. All affected documentation must be updated

**Compliance & Reviews**:
- All pull requests MUST demonstrate compliance with constitution principles
- Quarterly review of constitution effectiveness and relevance
- Violations require documented exception approval or immediate remediation

**Versioning Policy**:
- **MAJOR**: Backward-incompatible changes, principle removals/redefinitions
- **MINOR**: New principles or sections added, material expansions
- **PATCH**: Clarifications, wording improvements, non-semantic changes

**Version**: 1.0.0 | **Ratified**: 2025-11-22 | **Last Amended**: 2025-11-22
