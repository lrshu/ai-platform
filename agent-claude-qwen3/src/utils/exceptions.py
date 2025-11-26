"""
Error handling and logging infrastructure.
"""

import logging
import traceback
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class OnboardingError(Exception):
    """Base exception for onboarding system errors."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(OnboardingError):
    """Exception raised for validation errors."""
    pass

class DatabaseError(OnboardingError):
    """Exception raised for database errors."""
    pass

class ExternalServiceError(OnboardingError):
    """Exception raised for external service errors."""
    pass

class AuthenticationError(OnboardingError):
    """Exception raised for authentication errors."""
    pass

def log_error(error: Exception, context: Optional[str] = None):
    """
    Log an error with context and traceback.

    Args:
        error: The exception to log
        context: Optional context information
    """
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg = f"{context} - {error_msg}"

    logger.error(error_msg)
    logger.error(f"Traceback: {traceback.format_exc()}")

def log_info(message: str, context: Optional[str] = None):
    """
    Log an info message with optional context.

    Args:
        message: The message to log
        context: Optional context information
    """
    if context:
        message = f"{context} - {message}"
    logger.info(message)

def log_warning(message: str, context: Optional[str] = None):
    """
    Log a warning message with optional context.

    Args:
        message: The message to log
        context: Optional context information
    """
    if context:
        message = f"{context} - {message}"
    logger.warning(message)