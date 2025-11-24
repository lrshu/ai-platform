"""
Unit tests for the security module.
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.lib.security import (
    SecurityManager, SecurityError, InvalidTokenError, ExpiredTokenError,
    RateLimitExceededError, get_security_manager, require_secure_token
)


class TestSecurityManager:
    """Test the SecurityManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.secret_key = "test_secret_key"
        self.security_manager = SecurityManager(self.secret_key)

    def test_init(self):
        """Test initialization."""
        assert self.security_manager.secret_key == b"test_secret_key"

    def test_generate_token(self):
        """Test token generation."""
        token = self.security_manager.generate_token("test_data")
        assert isinstance(token, str)
        assert len(token) > 0
        assert ":" in token

    def test_validate_token_success(self):
        """Test successful token validation."""
        token = self.security_manager.generate_token("test_data")
        data = self.security_manager.validate_token(token)
        assert data == "test_data"

    def test_validate_token_malformed(self):
        """Test validation of malformed token."""
        with pytest.raises(InvalidTokenError):
            self.security_manager.validate_token("malformed_token")

    def test_validate_token_invalid_signature(self):
        """Test validation of token with invalid signature."""
        # Create a token with wrong signature
        token = "test_data:9999999999:invalid_signature"
        with pytest.raises(InvalidTokenError):
            self.security_manager.validate_token(token)

    def test_validate_token_expired(self):
        """Test validation of expired token."""
        # Create a token that expires immediately
        token = self.security_manager.generate_token("test_data", expires_in=-1)
        with pytest.raises((ExpiredTokenError, InvalidTokenError)):
            self.security_manager.validate_token(token)

    def test_generate_secure_id(self):
        """Test secure ID generation."""
        secure_id = self.security_manager.generate_secure_id()
        assert isinstance(secure_id, str)
        assert len(secure_id) == 32  # 16 bytes = 32 hex characters

        secure_id_with_prefix = self.security_manager.generate_secure_id("prefix_")
        assert secure_id_with_prefix.startswith("prefix_")

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password"
        hashed_password, salt = self.security_manager.hash_password(password)

        assert isinstance(hashed_password, str)
        assert isinstance(salt, str)
        assert len(hashed_password) == 64  # SHA-256 hex = 64 characters
        assert len(salt) == 32  # 16 bytes = 32 hex characters

    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "test_password"
        hashed_password, salt = self.security_manager.hash_password(password)
        result = self.security_manager.verify_password(password, hashed_password, salt)
        assert result is True

    def test_verify_password_failure(self):
        """Test failed password verification."""
        password = "test_password"
        wrong_password = "wrong_password"
        hashed_password, salt = self.security_manager.hash_password(password)
        result = self.security_manager.verify_password(wrong_password, hashed_password, salt)
        assert result is False

    def test_sanitize_input(self):
        """Test input sanitization."""
        # Test normal input
        clean_input = "This is a clean input"
        result = self.security_manager.sanitize_input(clean_input)
        assert result == clean_input

        # Test input with dangerous characters
        dirty_input = "<script>alert('xss')</script>"
        result = self.security_manager.sanitize_input(dirty_input)
        assert "<" not in result
        assert ">" not in result
        # Note: The basic implementation just removes characters, so "script" might still appear
        # In a real implementation, we'd use a proper sanitization library

        # Test input length limit
        long_input = "a" * 1500
        result = self.security_manager.sanitize_input(long_input)
        assert len(result) == 1000

    def test_check_rate_limit_success(self):
        """Test successful rate limit check."""
        result = self.security_manager.check_rate_limit("test_resource", "test_client", 5, 60)
        assert result is True

    def test_check_rate_limit_exceeded(self):
        """Test rate limit exceeded."""
        # Make 5 requests (limit is 5)
        for i in range(5):
            self.security_manager.check_rate_limit("test_resource", "test_client", 5, 60)

        # 6th request should fail
        with pytest.raises(RateLimitExceededError):
            self.security_manager.check_rate_limit("test_resource", "test_client", 5, 60)

    def test_generate_api_key(self):
        """Test API key generation."""
        api_key = self.security_manager.generate_api_key()
        assert isinstance(api_key, str)
        assert api_key.startswith("sk_")
        assert len(api_key) == 35  # "sk_" + 32 hex characters

    def test_validate_api_key_success(self):
        """Test successful API key validation."""
        api_key = self.security_manager.generate_api_key()
        result = self.security_manager.validate_api_key(api_key)
        assert result is True

    def test_validate_api_key_invalid_format(self):
        """Test API key validation with invalid format."""
        # Test wrong prefix
        result = self.security_manager.validate_api_key("ak_1234567890abcdef")
        assert result is False

        # Test wrong length
        result = self.security_manager.validate_api_key("sk_12345")
        assert result is False

        # Test invalid hex
        result = self.security_manager.validate_api_key("sk_1234567890xyz!")
        assert result is False

        # Test non-string input
        result = self.security_manager.validate_api_key(12345)
        assert result is False


class TestSecurityFunctions:
    """Test the security functions."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Reset the global security manager
        global _security_manager
        _security_manager = None

    def test_get_security_manager(self):
        """Test getting the security manager."""
        manager1 = get_security_manager()
        manager2 = get_security_manager()
        assert manager1 is manager2

    def test_require_secure_token(self):
        """Test the require_secure_token decorator."""
        security_manager = get_security_manager()
        token = security_manager.generate_token("test_data")

        @require_secure_token(token)
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    def test_require_secure_token_invalid(self):
        """Test the require_secure_token decorator with invalid token."""
        invalid_token = "invalid_token"

        @require_secure_token(invalid_token)
        def test_function():
            return "success"

        with pytest.raises(InvalidTokenError):
            test_function()


if __name__ == "__main__":
    pytest.main([__file__])