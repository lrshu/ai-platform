# Quickstart — New Hire Onboarding Multi-Agent Backend

## Prerequisites
- Python 3.12 with `uv` installed
- MCP servers for email (`http://127.0.0.1:9012/mcp/email`) and git (`http://127.0.0.1:9012/mcp/git`)
- Qwen API credentials with access to qwen3-max and qwen3-vl-max
- LangSmith project API key for tracing

## Setup Steps
1. **Install dependencies**
   ```bash
   uv sync
   ```
2. **Copy environment template**
   ```bash
   cp .env.example .env
   ```
   Populate the following keys:
   - `QWEN_API_BASE`, `QWEN_API_KEY`
   - `MCP_SERVER`
   - `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`
3. **Seed role knowledge assets**
   ```bash
   python scripts/seed_role_assets.py --file data/role_assets.json
   ```
4. **Launch onboarding chat**
   ```bash
   python main.py chat
   ```
   Use the CLI prompts to simulate a new hire session.

## Running Tests
- **Unit tests**
  ```bash
  uv run pytest tests/unit
  ```
- **Contract tests (MCP payloads)**
  ```bash
  uv run pytest tests/contract
  ```
- **Integration test (full flow)**
  ```bash
  uv run pytest tests/integration/test_onboarding_flow.py
  ```
  The integration suite spins up mock MCP servers defined in `tests/integration/fixtures/mcp_servers.py` and replays scripted conversations from `tests/integration/fixtures/onboarding_happy_path.jsonl`.

## Troubleshooting
- Missing environment variable: run `uv run python scripts/verify_env.py` to check required keys.
- MCP server unreachable: ensure the local MCP mock is running or update `MCP_SERVER` to the correct endpoint.
- Identity validation failures: verify sample ID images are accessible and contain readable text; logs stored in `logs/identity/*.log`.
