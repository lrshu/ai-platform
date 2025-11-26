# Phase 0 Research Log — New Hire Onboarding Multi-Agent Backend

## Identity Verification Modality
- **Decision**: Leverage Qwen3-VL-Max via LangChain multimodal tool wrapper for ID photo validation and OCR extraction.
- **Rationale**: Qwen3-VL-Max natively handles Chinese IDs, supports instruction following for quality feedback, and integrates with LangChain’s DeepAgents action model. Keeps LLM + VL stack consistent (Qwen family) to simplify auth and rate limiting.
- **Alternatives Considered**:
  - *Third-party OCR API (e.g., Baidu AI Cloud)* — rejected due to extra vendor dependency and inconsistent deployment story.
  - *Local OCR (Tesseract)* — insufficient accuracy on Chinese resident ID formatting and requires heavier DevOps footprint.

## Data Persistence Strategy
- **Decision**: Store onboarding sessions, profiles, and provisioning artifacts in SQLite through SQLModel (async) with encrypted columns for sensitive identity data.
- **Rationale**: SQLite works seamlessly with uv-managed local runtime, supports migrations/testing without extra services, and SQLModel keeps schemas close to Pydantic validation used by agents.
- **Alternatives Considered**:
  - *PostgreSQL* — overkill for single-node workflow and raises setup burden for local integration tests.
  - *Document store (MongoDB)* — weaker transactional guarantees for checklist state transitions.

## Agent Orchestration Framework Alignment
- **Decision**: Build LangGraph workflow orchestrating DeepAgents sub-graphs for each role, using shared memory/state classes for checklist and profile data.
- **Rationale**: LangGraph supplies deterministic node execution, state serialization, and built-in testing harness. DeepAgents fits multi-agent pattern and is explicitly requested.
- **Alternatives Considered**:
  - *Plain LangChain chains* — insufficient for complex branching plus concurrency control.
  - *Custom asyncio orchestration* — increases bespoke code without extra benefit.

## MCP Tooling Strategy
- **Decision**: Use MCP client SDK to call two external servers (`email_provisioner`, `git_provisioner`) selected dynamically based on role taxonomy stored in role assets table.
- **Rationale**: Aligns with requirement for MCP tool agent; decouples provisioning logic, allows mocking via local MCP test servers for integration tests.
- **Alternatives Considered**:
  - *Direct REST calls* — would violate requirement to use MCP tooling agent.
  - *Manual admin queue* — would lengthen onboarding and fail success metrics.

## Testing Approach
- **Decision**: Author integration test that runs `python main.py chat --script fixtures/onboarding_happy_path.jsonl` using LangGraph testing harness to simulate conversation; add contract tests for MCP payload schemas and unit tests for checklist + validation helpers.
- **Rationale**: Ensures red-green coverage across conversation, contracts, and business logic per constitution. JSONL fixture keeps deterministic prompts/responses.
- **Alternatives Considered**:
  - *Manual smoke tests only* — fails Test Discipline principle.
  - *Unit tests without integration coverage* — cannot validate multi-agent orchestration or MCP calls.

## .env Configuration
- **Decision**: Ship `.env.example` with placeholders for QWen, LangSmith, and MCP endpoints; add `scripts/verify_env.py` to assert required keys before runtime.
- **Rationale**: Meets user request for generated env file while preventing accidental leakage; verification script helps CI catch missing secrets early.
- **Alternatives Considered**:
  - *Direct `.env` with real secrets* — security risk.
  - *Config via CLI flags only* — cumbersome and error-prone for multi-service setup.
