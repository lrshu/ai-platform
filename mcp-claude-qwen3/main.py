"""
Main application entry point for the MCP Account Provisioning Server.

This module initializes and starts the FastAPI application for provisioning
email and git accounts based on Chinese names and ID numbers.
"""
import uvicorn
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api import create_app
from src.api.routes import setup_routes
from src.config import PORT, HOST
from fastapi_mcp import FastApiMCP


def main() -> None:
    """
    Main application entry point.

    Creates the FastAPI application, sets up routes, and starts the server
    using uvicorn.

    The server will listen on the host and port specified in the configuration.
    """
    # Create FastAPI app
    app = create_app()

    # Set up routes
    setup_routes(app)

    mcp = FastApiMCP(app, describe_all_responses=True, headers=["authorization", "authentication", "x-api-key", "api-key", "x-token", "token"])
    mcp.mount_http()
    mcp.mount_sse()

    # Run the application
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()