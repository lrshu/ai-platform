from __future__ import annotations

import logging
from fastapi import FastAPI
from fastapi_mcp import MCPServer

from server.audit import create_audit_logger
from server.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
    app = FastAPI(title="MCP Account Provisioning Server")
    app.state.settings = settings
    app.state.audit_logger = create_audit_logger()
    return app


def create_mcp_server(app: FastAPI) -> MCPServer:
    return MCPServer(app)


def main() -> None:
    app = create_app()
    mcp_server = create_mcp_server(app)
    mcp_server.run()


if __name__ == "__main__":
    main()
