<!-- Sync Impact Report:
Version change: 1.0.0 → 1.0.0
Modified principles: None (new constitution)
Added sections: Core Principles, Development Standards, Performance Requirements, Governance
Removed sections: None
Templates requiring updates: ✅ Updated .specify/templates/plan-template.md
                        ✅ Updated .specify/templates/spec-template.md
                        ✅ Updated .specify/templates/tasks-template.md
                        ✅ Updated .specify/templates/agent-file-template.md
Follow-up TODOs: None
-->

# MCP Claude Qwen3 Constitution

## Core Principles

### I. Code Quality Standards
All code MUST adhere to established quality standards including:
- Consistent naming conventions aligned with language idioms
- Comprehensive documentation for public APIs and complex logic
- Adherence to SOLID principles where applicable
- Regular code reviews with focus on maintainability and clarity
- Elimination of code smells and technical debt before merging

Rationale: High-quality code reduces maintenance burden, improves team velocity, and ensures long-term project sustainability.

### II. Testing Excellence
Every feature MUST be accompanied by appropriate tests:
- Unit tests covering core business logic with minimum 80% coverage
- Integration tests for all external service interactions
- End-to-end tests for critical user journeys
- Property-based testing for complex algorithms where applicable
- Test-driven development (TDD) encouraged but not mandated

Rationale: Comprehensive testing ensures reliability, enables safe refactoring, and prevents regressions.

### III. User Experience Consistency
All user-facing elements MUST maintain consistent experience:
- Unified design language across all interfaces
- Consistent terminology and messaging patterns
- Accessible interfaces following WCAG guidelines
- Responsive design principles applied consistently
- User feedback incorporated through usability testing

Rationale: Consistent UX reduces cognitive load, increases user satisfaction, and strengthens brand perception.

### IV. Performance Optimization
All implementations MUST meet defined performance criteria:
- Response times under 200ms for 95th percentile of requests
- Memory consumption optimized for target deployment environments
- Database queries optimized with proper indexing strategies
- Asynchronous processing for non-critical operations
- Regular performance benchmarking and monitoring

Rationale: Optimal performance enhances user experience, reduces infrastructure costs, and supports scalability.

## Development Standards

### Code Review Process
- All changes MUST undergo peer review before merging
- Reviewers MUST verify adherence to constitution principles
- Automated checks MUST pass before review begins
- Reviews MUST be completed within 24 hours of request
- Complex changes require architectural review

### Documentation Requirements
- Public APIs MUST include comprehensive documentation
- Significant changes MUST update relevant documentation
- README files MUST accurately reflect current state
- Inline comments MUST explain "why" not just "what"
- Architecture decisions MUST be recorded as ADRs

### Version Control Standards
- Feature branches MUST be used for all development
- Commits MUST follow conventional commit format
- Pull requests MUST include descriptive summaries
- Main branch MUST remain deployable at all times
- Breaking changes MUST follow semantic versioning

## Performance Requirements

### Response Time Benchmarks
- API endpoints: 95th percentile < 200ms
- Database queries: 95th percentile < 100ms
- Page loads: 95th percentile < 1000ms
- Background jobs: Completion within SLA timeframe

### Resource Utilization Limits
- CPU usage: < 70% average during peak load
- Memory usage: < 80% of allocated resources
- Database connections: Efficient pooling and reuse
- Network I/O: Minimized through caching and batching

### Monitoring and Alerting
- Key metrics MUST be instrumented and tracked
- Automated alerts MUST trigger for performance degradation
- Performance data MUST be retained for trend analysis
- Regular performance reviews MUST be conducted

## Governance

### Amendment Process
- Proposed changes MUST be documented with rationale
- Community review period of minimum 7 days required
- Changes MUST be approved by project maintainers
- Major changes require demonstration of impact
- All amendments MUST be backward compatible when possible

### Compliance Verification
- Constitution adherence MUST be verified during code reviews
- Automated tools SHOULD enforce applicable standards
- Violations MUST be justified with clear documentation
- Regular audits MUST be conducted to ensure compliance

### Versioning Policy
- MAJOR: Backward incompatible governance/principle removals or redefinitions
- MINOR: New principle/section added or materially expanded guidance
- PATCH: Clarifications, wording, typo fixes, non-semantic refinements

**Version**: 1.0.0 | **Ratified**: 2025-11-26 | **Last Amended**: 2025-11-26