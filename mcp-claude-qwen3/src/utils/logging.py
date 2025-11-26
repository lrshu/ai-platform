"""
Logging infrastructure for the MCP Account Provisioning Server.
"""
import logging
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime


def setup_logging() -> logging.Logger:
    """
    Set up logging configuration for the application.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("mcp_account_provisioning")
    logger.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


def log_provisioning_event(logger: logging.Logger, event_type: str, name: str, account_type: str, success: bool = True, error_message: str = None):
    """
    Log a provisioning event.

    Args:
        logger (logging.Logger): Logger instance
        event_type (str): Type of event (e.g., "email_provisioning", "git_provisioning", "batch_provisioning")
        name (str): Name of the person
        account_type (str): Type of account being provisioned
        success (bool): Whether the provisioning was successful
        error_message (str): Error message if provisioning failed
    """
    if success:
        logger.info(f"{event_type}: Successfully provisioned {account_type} account for {name}")
    else:
        logger.error(f"{event_type}: Failed to provision {account_type} account for {name}. Error: {error_message}")


# Initialize logger
logger = setup_logging()