"""
Configuration management for the MCP Account Provisioning Server.

This module handles loading and providing configuration values from environment
variables and default values.
"""
import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server configuration
PORT: int = int(os.getenv("PORT", 9102))
"""The port number on which the server will listen. Defaults to 9102."""

HOST: str = os.getenv("HOST", "0.0.0.0")
"""The host address on which the server will listen. Defaults to '0.0.0.0'."""

# Application configuration
APP_TITLE: str = "MCP Account Provisioning Server"
"""The title of the application."""

APP_DESCRIPTION: str = "Service for provisioning email and git accounts based on Chinese names and ID numbers"
"""The description of the application."""