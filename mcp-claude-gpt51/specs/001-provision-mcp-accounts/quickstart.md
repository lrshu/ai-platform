# Quickstart — MCP Account Provisioning Server

## Prerequisites
- Python 3.12+ installed with [uv](https://github.com/astral-sh/uv)
- `fastapi-mcp`, `pypinyin`, `python-dotenv`, `pydantic`, `pytest`, `httpx`, `anyio` specified in `pyproject.toml`
- `.env` file configured (see below) or fallback `.env.example`

## Setup Steps
1. **Install dependencies**
   ```bash
   uv pip install -r pyproject.toml
   ```
2. **Configure environment**
   - Copy `.env.example` to `.env`.
   - Set variables:
     ```env
     PORT=9102
     LOG_LEVEL=INFO
     ```
3. **Run lint + tests (required before dev server)**
   ```bash
   uv run ruff check .
   uv run pyright
   uv run pytest
   ```

## Running the MCP Server
```bash
uv run python main.py
```
The server loads MCP tools registered under `email_account` and `git_account`. Confirm startup logs show both tools ready and listening on `PORT`.

## Integration Testing Workflow
1. Start the server in one terminal or rely on application factory for in-process tests.
2. Run integration suite:
   ```bash
   uv run pytest tests/integration/test_provisioning.py -q
   ```
3. Tests cover:
   - Valid email/git provisioning flows
   - Invalid ID checksum responses
   - Transliteration failures
   - Configuration errors (missing env)

## Observability & Logs
- Audit events emitted through standard logging with masked IDs and `audit_id` references.
- Use `LOG_LEVEL=DEBUG` to inspect validation traces when debugging.

## Troubleshooting
| Symptom | Resolution |
| --- | --- |
| Server exits with config error | Ensure `.env` exists and `PORT` is numeric. |
| Tests fail on transliteration | Verify name input contains supported Hanzi; update custom overrides. |
| Password policy assertions fail | Confirm `secrets` module is used and all character classes are enforced. |
| Integration tests hang | Ensure no other service is holding the configured `PORT`; kill stale processes. |

## Next Steps
- After verifying quickstart, proceed to `/speckit.tasks` to generate implementation tasks.
