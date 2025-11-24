"""
Security utilities for the RAG backend system.
"""

import hashlib
import hmac
import secrets
import time
from typing import Optional, Dict, Any
from src.lib.exceptions import RAGBaseException


class SecurityError(RAGBaseException):
    """Base class for security-related exceptions."""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidTokenError(SecurityError):
    """Raised when a security token is invalid."""

    def __init__(self, message: str = "Invalid security token"):
        super().__init__(message)


class ExpiredTokenError(SecurityError):
    """Raised when a security token has expired."""

    def __init__(self, message: str = "Security token has expired"):
        super().__init__(message)


class RateLimitExceededError(SecurityError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message)


class SecurityManager:
    """
    Manages security-related functionality including token generation,
    validation, and rate limiting.
    """

    def __init__(self, secret_key: str):
        """
        Initialize the security manager.

        Args:
            secret_key: Secret key used for token generation and validation
        """
        self.secret_key = secret_key.encode('utf-8') if isinstance(secret_key, str) else secret_key
        self._rate_limits: Dict[str, Dict[str, Any]] = {}

    def generate_token(self, data: str, expires_in: int = 3600) -> str:
        """
        Generate a secure token with expiration.

        Args:
            data: Data to include in the token
            expires_in: Token expiration time in seconds (default: 1 hour)

        Returns:
            Secure token string
        """
        # Create expiration timestamp
        expires_at = int(time.time()) + expires_in

        # Create message to sign
        message = f"{data}:{expires_at}"

        # Create HMAC signature
        signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Combine data, expiration, and signature
        token = f"{data}:{expires_at}:{signature}"
        return token

    def validate_token(self, token: str) -> str:
        """
        Validate a token and return the embedded data.

        Args:
            token: Token to validate

        Returns:
            Data embedded in the token

        Raises:
            InvalidTokenError: If token is invalid
            ExpiredTokenError: If token has expired
        """
        try:
            # Split token into components
            parts = token.split(':')
            if len(parts) != 3:
                raise InvalidTokenError("Malformed token")

            data, expires_at_str, signature = parts
            expires_at = int(expires_at_str)

            # Check expiration
            if time.time() > expires_at:
                raise ExpiredTokenError()

            # Recreate message and signature
            message = f"{data}:{expires_at}"
            expected_signature = hmac.new(
                self.secret_key,
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Verify signature using constant-time comparison
            if not hmac.compare_digest(signature, expected_signature):
                raise InvalidTokenError("Invalid token signature")

            return data

        except ValueError:
            raise InvalidTokenError("Invalid token format")
        except InvalidTokenError:
            raise
        except Exception:
            raise InvalidTokenError("Token validation failed")

    def generate_secure_id(self, prefix: str = "") -> str:
        """
        Generate a cryptographically secure random ID.

        Args:
            prefix: Optional prefix for the ID

        Returns:
            Secure random ID
        """
        random_bytes = secrets.token_bytes(16)
        hex_string = random_bytes.hex()
        return f"{prefix}{hex_string}" if prefix else hex_string

    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Hash a password with a salt.

        Args:
            password: Password to hash
            salt: Optional salt (generated if not provided)

        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # Create hash using PBKDF2
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        ).hex()

        return password_hash, salt

    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            password: Password to verify
            hashed_password: Hashed password to compare against
            salt: Salt used in hashing

        Returns:
            True if password matches, False otherwise
        """
        computed_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, hashed_password)

    def sanitize_input(self, input_str: str) -> str:
        """
        Sanitize user input to prevent injection attacks.

        Args:
            input_str: Input string to sanitize

        Returns:
            Sanitized string
        """
        if not isinstance(input_str, str):
            return str(input_str)

        # Remove or escape dangerous characters
        # This is a basic implementation - in production, use a proper library
        dangerous_chars = ['<', '>', '&', '"', "'", ';', '--', '/*', '*/']
        sanitized = input_str

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        # Limit length
        return sanitized[:1000]  # Limit to 1000 characters

    def check_rate_limit(self, resource: str, identifier: str, max_requests: int = 100,
                        window_seconds: int = 3600) -> bool:
        """
        Check if a rate limit has been exceeded.

        Args:
            resource: Resource being accessed
            identifier: Identifier for the client (e.g., IP address, user ID)
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False if rate limit exceeded

        Raises:
            RateLimitExceededError: If rate limit is exceeded
        """
        key = f"{resource}:{identifier}"
        now = time.time()

        if key not in self._rate_limits:
            self._rate_limits[key] = {
                'requests': [],
                'window_start': now
            }

        rate_limit = self._rate_limits[key]

        # Remove old requests outside the window
        rate_limit['requests'] = [
            timestamp for timestamp in rate_limit['requests']
            if now - timestamp < window_seconds
        ]

        # Check if we're under the limit
        if len(rate_limit['requests']) < max_requests:
            rate_limit['requests'].append(now)
            return True

        raise RateLimitExceededError(f"Rate limit exceeded for {resource}")

    def generate_api_key(self) -> str:
        """
        Generate a secure API key.

        Returns:
            Secure API key
        """
        return self.generate_secure_id("sk_")

    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate an API key format (basic validation).

        Args:
            api_key: API key to validate

        Returns:
            True if API key format is valid, False otherwise
        """
        if not isinstance(api_key, str):
            return False

        if not api_key.startswith("sk_"):
            return False

        if len(api_key) != 35:  # "sk_" + 32 hex characters
            return False

        # Check if the rest is valid hex
        try:
            bytes.fromhex(api_key[3:])
            return True
        except ValueError:
            return False


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """
    Get the global security manager instance.

    Returns:
        SecurityManager instance
    """
    global _security_manager
    if _security_manager is None:
        # Generate a secure secret key if not provided
        secret_key = secrets.token_hex(32)
        _security_manager = SecurityManager(secret_key)
    return _security_manager


def require_secure_token(token: str):
    """
    Decorator to require a valid security token for function execution.

    Args:
        token: Token to validate
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            security_manager = get_security_manager()
            security_manager.validate_token(token)
            return func(*args, **kwargs)
        return wrapper
    return decorator