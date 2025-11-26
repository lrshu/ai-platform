# MCP Account Provisioning Server

This project implements a FastAPI-based MCP server that provisions deterministic email and git credentials from a Chinese name plus national ID. It follows the specification in `specs/001-provision-mcp-accounts/`.

## Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management

## Setup
```bash
uv pip install -r pyproject.toml
cp .env.example .env  # adjust PORT, LOG_LEVEL, and optional overrides
```

## Development workflow
- Lint: `uv run ruff check .`
- Format: `uv run black .`
- Type check: `uv run pyright`
- Tests: `uv run pytest`

## Running the server
```bash
uv run python main.py
```

## CLI entry point
The MCP server exposes tools defined in `server/tools/` via `main.py`. See `specs/001-provision-mcp-accounts/quickstart.md` for integration scenarios.
