# Implementation Plan: MCP Account Provisioning Server

**Branch**: `001-provision-mcp-accounts` | **Date**: 2025-11-25 | **Spec**: [specs/001-provision-mcp-accounts/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-provision-mcp-accounts/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a fastapi-mcp powered server that offers two provisioning tools—`email_account` and `git_account`—which accept a Chinese name plus national ID, validate identity numbers, transliterate names to lowercase pinyin, and return deterministic handles with randomized onboarding passwords. The delivery scope also covers configuration management via `.env`, comprehensive integration testing, and automated validation of ID correctness, audit logging, and performance targets defined in the spec.

## Technical Context

**Language/Version**: Python 3.12 (uv-managed virtual environment)
**Primary Dependencies**: `fastapi-mcp` for MCP server scaffolding, `pydantic` for validation, `pypinyin` (or equivalent) for transliteration, `python-dotenv` for configuration loading, `secrets`/`uvicorn` runtime utilities
**Storage**: None (stateless service; audit entries streamed to logs)
**Testing**: `pytest` + `httpx` + `anyio` for async integration tests; `pytest-cov` for coverage gates
**Target Platform**: POSIX hosts running uv/virtualenv (validated on macOS + Linux CI)
**Project Type**: Single-service backend with CLI entry `python main.py`
**Performance Goals**: 95% of provisioning calls complete <3s; ID validation + transliteration <200ms per request; zero credential leakage for invalid inputs
**Constraints**: Must enforce constitution principles—lint + type checks before merge, deterministic handles, accessibility-friendly error messaging (plain language, localized), perf regressions <5% vs baseline
**Scale/Scope**: Supports concurrent onboarding bursts (~100 requests/minute) without shared state; two MCP tools with shared validation pipeline

## Constitution Check

1. **Verifiable Code Quality**
   - Plan includes formatting (ruff/black) and type checking (pyright) prior to PR.
   - Shared validators and password generators will ship with docstrings describing contracts.
2. **Test Discipline & Coverage**
   - Integration tests for both tools will be authored before implementation (Red-Green).
   - CI will execute pytest + coverage; failures block merge.
3. **Consistent User Experience**
   - Error payloads standardized (code, message, remediation) and localized-ready.
   - Deterministic handle generation ensures UX parity between tools.
4. **Performance & Resource Guarantees**
   - Plan captures latency budgets plus profiling hooks via timing logs.
   - `.env`-driven config enables resource tuning; regressions >5% trigger rollback.

*Gate Result*: PASS — each constitutional obligation mapped to concrete tasks (see Phases).

## Project Structure

### Documentation (this feature)

```text
specs/001-provision-mcp-accounts/
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 research outputs
├── data-model.md        # Entity definitions & validation rules
├── quickstart.md        # Runbook for devs/testers
├── contracts/           # API/MCP contract artifacts
└── tasks.md             # Generated later via /speckit.tasks
```

### Source Code (repository root)

```text
.
├── .env.example               # Template generated in this feature
├── main.py                    # FastAPI-MCP server entrypoint
├── server/
│   ├── __init__.py
│   ├── config.py              # Env loading & validation
│   ├── id_validator.py        # Chinese ID algorithm + errors
│   ├── transliteration.py     # Pinyin conversion helpers
│   ├── password.py            # Credential generator utilities
│   └── tools/
│       ├── email_tool.py      # email_account MCP tool definition
│       └── git_tool.py        # git_account MCP tool definition
├── tests/
│   ├── __init__.py
│   ├── integration/
│   │   └── test_provisioning.py
│   └── fixtures/
│       └── __init__.py
└── uv.lock / pyproject.toml   # Dependency manifests
```

**Structure Decision**: Single Python service with modularized helpers under `server/` keeps shared validation logic centralized while enabling focused unit and integration tests. Tests use `tests/integration/test_provisioning.py` to drive MCP client flows via HTTP layer.

## Complexity Tracking

_Not required at this time—no constitution violations identified._
