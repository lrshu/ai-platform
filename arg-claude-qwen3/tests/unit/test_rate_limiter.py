"""
Unit tests for the rate limiting module.
"""

import pytest
import time
from unittest.mock import Mock
from src.lib.rate_limiter import (
    TokenBucketRateLimiter, SlidingWindowRateLimiter, RateLimiterManager,
    RateLimitExceededError, get_rate_limiter_manager,
    rate_limit_by_token_bucket, rate_limit_by_sliding_window
)


class TestTokenBucketRateLimiter:
    """Test the TokenBucketRateLimiter class."""

    def test_init(self):
        """Test initialization."""
        limiter = TokenBucketRateLimiter(10, 1.0)
        assert limiter.capacity == 10
        assert limiter.refill_rate == 1.0
        assert limiter.tokens == 10

    def test_consume_success(self):
        """Test successful token consumption."""
        limiter = TokenBucketRateLimiter(10, 1.0)
        result = limiter.consume(5)
        assert result is True
        assert limiter.tokens == 5

    def test_consume_failure(self):
        """Test failed token consumption."""
        limiter = TokenBucketRateLimiter(10, 1.0)
        limiter.tokens = 2
        result = limiter.consume(5)
        assert result is False
        assert abs(limiter.tokens - 2) < 0.0001  # Allow for floating point precision

    def test_refill_tokens(self):
        """Test token refilling."""
        limiter = TokenBucketRateLimiter(10, 10.0)  # 10 tokens per second
        limiter.tokens = 0
        limiter.last_refill = time.time() - 0.5  # 500ms ago

        # Consume should trigger refill
        result = limiter.consume(3)
        assert result is True
        assert limiter.tokens >= 2  # Should have ~2 tokens after refill

    def test_wait_and_consume_success(self):
        """Test waiting and consuming tokens successfully."""
        limiter = TokenBucketRateLimiter(5, 10.0)  # Fast refill rate
        limiter.tokens = 0

        # Should succeed quickly due to fast refill
        result = limiter.wait_and_consume(1, timeout=0.2)
        assert result is True

    def test_wait_and_consume_timeout(self):
        """Test waiting and consuming tokens with timeout."""
        limiter = TokenBucketRateLimiter(1, 0.1)  # Slow refill rate
        limiter.tokens = 0

        # Should timeout due to slow refill
        result = limiter.wait_and_consume(5, timeout=0.1)
        assert result is False


class TestSlidingWindowRateLimiter:
    """Test the SlidingWindowRateLimiter class."""

    def test_init(self):
        """Test initialization."""
        limiter = SlidingWindowRateLimiter(10, 60.0)
        assert limiter.max_requests == 10
        assert limiter.window_size == 60.0

    def test_is_allowed_success(self):
        """Test successful request allowance."""
        limiter = SlidingWindowRateLimiter(3, 1.0)  # 3 requests per second
        result = limiter.is_allowed("client1")
        assert result is True

    def test_is_allowed_failure(self):
        """Test request rejection due to rate limit."""
        limiter = SlidingWindowRateLimiter(2, 1.0)  # 2 requests per second

        # First two requests should be allowed
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True

        # Third request should be rejected
        assert limiter.is_allowed("client1") is False

    def test_window_cleanup(self):
        """Test cleanup of old requests outside window."""
        limiter = SlidingWindowRateLimiter(2, 0.1)  # Small window

        # Make requests
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True

        # Wait for window to expire
        time.sleep(0.15)

        # New request should be allowed (old requests cleaned up)
        assert limiter.is_allowed("client1") is True


class TestRateLimiterManager:
    """Test the RateLimiterManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Reset the global rate limiter manager
        global _rate_limiter_manager
        _rate_limiter_manager = None

    def test_get_rate_limiter_manager(self):
        """Test getting the rate limiter manager."""
        manager1 = get_rate_limiter_manager()
        manager2 = get_rate_limiter_manager()
        assert manager1 is manager2

    def test_add_token_bucket_limiter(self):
        """Test adding a token bucket limiter."""
        manager = get_rate_limiter_manager()
        manager.add_token_bucket_limiter("test_limiter", 10, 1.0)
        assert "test_limiter" in manager.limiters

    def test_add_sliding_window_limiter(self):
        """Test adding a sliding window limiter."""
        manager = get_rate_limiter_manager()
        manager.add_sliding_window_limiter("test_limiter", 10, 60.0)
        assert "test_limiter" in manager.window_limiters

    def test_check_token_bucket_limit_success(self):
        """Test checking token bucket limit successfully."""
        manager = get_rate_limiter_manager()
        manager.add_token_bucket_limiter("test_limiter", 10, 1.0)
        result = manager.check_token_bucket_limit("test_limiter", 1)
        assert result is True

    def test_check_token_bucket_limit_failure(self):
        """Test checking token bucket limit failure."""
        manager = get_rate_limiter_manager()
        manager.add_token_bucket_limiter("test_limiter", 1, 1.0)
        manager.limiters["test_limiter"].tokens = 0

        with pytest.raises(RateLimitExceededError):
            manager.check_token_bucket_limit("test_limiter", 1)

    def test_check_sliding_window_limit_success(self):
        """Test checking sliding window limit successfully."""
        manager = get_rate_limiter_manager()
        manager.add_sliding_window_limiter("test_limiter", 10, 60.0)
        result = manager.check_sliding_window_limit("test_limiter", "client1")
        assert result is True

    def test_check_sliding_window_limit_failure(self):
        """Test checking sliding window limit failure."""
        manager = get_rate_limiter_manager()
        manager.add_sliding_window_limiter("test_limiter", 1, 1.0)

        # First request should succeed
        manager.check_sliding_window_limit("test_limiter", "client1")

        # Second request should fail
        with pytest.raises(RateLimitExceededError):
            manager.check_sliding_window_limit("test_limiter", "client1")

    def test_nonexistent_limiter(self):
        """Test checking limits with nonexistent limiter."""
        manager = get_rate_limiter_manager()
        # Should allow requests when limiter doesn't exist
        result = manager.check_token_bucket_limit("nonexistent", 1)
        assert result is True

        result = manager.check_sliding_window_limit("nonexistent", "client1")
        assert result is True


class TestRateLimitingDecorators:
    """Test the rate limiting decorators."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Reset the global rate limiter manager
        global _rate_limiter_manager
        _rate_limiter_manager = None

    def test_rate_limit_by_token_bucket(self):
        """Test token bucket rate limiting decorator."""
        manager = get_rate_limiter_manager()
        manager.add_token_bucket_limiter("test_function", 2, 10.0)  # High capacity

        @rate_limit_by_token_bucket("test_function", 1)
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    def test_rate_limit_by_token_bucket_exceeded(self):
        """Test token bucket rate limiting decorator with exceeded limit."""
        manager = get_rate_limiter_manager()
        manager.add_token_bucket_limiter("test_function", 1, 0.1)  # Low capacity
        manager.limiters["test_function"].tokens = 0

        @rate_limit_by_token_bucket("test_function", 1)
        def test_function():
            return "success"

        with pytest.raises(RateLimitExceededError):
            test_function()

    def test_rate_limit_by_sliding_window(self):
        """Test sliding window rate limiting decorator."""
        manager = get_rate_limiter_manager()
        manager.add_sliding_window_limiter("test_function", 10, 60.0)

        @rate_limit_by_sliding_window("test_function")
        def test_function(client_id):
            return f"success for {client_id}"

        result = test_function("client1")
        assert result == "success for client1"

    def test_rate_limit_by_sliding_window_exceeded(self):
        """Test sliding window rate limiting decorator with exceeded limit."""
        manager = get_rate_limiter_manager()
        manager.add_sliding_window_limiter("test_function", 1, 1.0)

        @rate_limit_by_sliding_window("test_function")
        def test_function(client_id):
            return f"success for {client_id}"

        # First call should succeed
        test_function("client1")

        # Second call should fail
        with pytest.raises(RateLimitExceededError):
            test_function("client1")


if __name__ == "__main__":
    pytest.main([__file__])