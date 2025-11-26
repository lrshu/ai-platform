# agent-claude-qwen3 Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-26

## Active Technologies

- Python 3.12+ (uv) + deepagents (under langchain), qwen3-max, qwen3-vl-max (001-employee-onboarding-agents)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12+ (uv): Follow standard conventions

## Constitution Principles

All development MUST adhere to the project constitution principles:

### Code Quality Standards
- Consistent naming conventions aligned with language idioms
- Comprehensive documentation for public APIs and complex logic
- Adherence to SOLID principles where applicable
- Regular code reviews with focus on maintainability and clarity

### Testing Excellence
- Unit tests covering core business logic with minimum 80% coverage
- Integration tests for all external service interactions
- End-to-end tests for critical user journeys
- Property-based testing for complex algorithms where applicable

### User Experience Consistency
- Unified design language across all interfaces
- Consistent terminology and messaging patterns
- Accessible interfaces following WCAG guidelines
- Responsive design principles applied consistently

### Performance Optimization
- Response times under 200ms for 95th percentile of requests
- Memory consumption optimized for target deployment environments
- Database queries optimized with proper indexing strategies
- Asynchronous processing for non-critical operations

## Recent Changes

- 001-employee-onboarding-agents: Added Python 3.12+ (uv) + deepagents (under langchain), qwen3-max, qwen3-vl-max

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
