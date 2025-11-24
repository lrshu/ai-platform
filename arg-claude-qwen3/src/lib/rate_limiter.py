"""
Rate limiting utilities for the RAG backend system.
"""

import time
import threading
from typing import Dict, Optional
from collections import defaultdict
from src.lib.exceptions import RAGBaseException


class RateLimitExceededError(RAGBaseException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message)


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter implementation.

    This rate limiter uses the token bucket algorithm to control the rate of requests.
    Tokens are added to the bucket at a fixed rate, and each request consumes one token.
    If there are no tokens available, the request is rejected.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize the token bucket rate limiter.

        Args:
            capacity: Maximum number of tokens in the bucket
            refill_rate: Number of tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        if elapsed > 0:
            new_tokens = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if rate limit would be exceeded
        """
        with self.lock:
            self._refill_tokens()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_and_consume(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Wait for tokens to become available and then consume them.

        Args:
            tokens: Number of tokens to consume
            timeout: Maximum time to wait in seconds (None for no timeout)

        Returns:
            True if tokens were consumed, False if timeout was reached
        """
        start_time = time.time()
        while True:
            if self.consume(tokens):
                return True

            if timeout is not None and (time.time() - start_time) >= timeout:
                return False

            # Sleep briefly to avoid busy waiting
            time.sleep(0.01)


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter implementation.

    This rate limiter tracks requests within a time window and limits the total
    number of requests in that window.
    """

    def __init__(self, max_requests: int, window_size: float):
        """
        Initialize the sliding window rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the window
            window_size: Size of the time window in seconds
        """
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        """
        Check if a request is allowed for the given key.

        Args:
            key: Identifier for the client/resource being rate limited

        Returns:
            True if request is allowed, False if rate limit would be exceeded
        """
        with self.lock:
            now = time.time()
            # Remove old requests outside the window
            self.requests[key] = [
                timestamp for timestamp in self.requests[key]
                if now - timestamp < self.window_size
            ]

            # Check if we're under the limit
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True

            return False


class RateLimiterManager:
    """Manages multiple rate limiters for different resources."""

    def __init__(self):
        """Initialize the rate limiter manager."""
        self.limiters: Dict[str, TokenBucketRateLimiter] = {}
        self.window_limiters: Dict[str, SlidingWindowRateLimiter] = {}
        self.lock = threading.Lock()

    def add_token_bucket_limiter(self, name: str, capacity: int, refill_rate: float) -> None:
        """
        Add a token bucket rate limiter.

        Args:
            name: Name of the rate limiter
            capacity: Maximum number of tokens in the bucket
            refill_rate: Number of tokens added per second
        """
        with self.lock:
            self.limiters[name] = TokenBucketRateLimiter(capacity, refill_rate)

    def add_sliding_window_limiter(self, name: str, max_requests: int, window_size: float) -> None:
        """
        Add a sliding window rate limiter.

        Args:
            name: Name of the rate limiter
            max_requests: Maximum number of requests allowed in the window
            window_size: Size of the time window in seconds
        """
        with self.lock:
            self.window_limiters[name] = SlidingWindowRateLimiter(max_requests, window_size)

    def check_token_bucket_limit(self, limiter_name: str, tokens: int = 1) -> bool:
        """
        Check if a request is allowed by a token bucket limiter.

        Args:
            limiter_name: Name of the rate limiter
            tokens: Number of tokens to consume

        Returns:
            True if request is allowed, False if rate limit would be exceeded

        Raises:
            RateLimitExceededError: If rate limit is exceeded
        """
        with self.lock:
            if limiter_name not in self.limiters:
                # No limiter configured, allow the request
                return True

            limiter = self.limiters[limiter_name]
            if not limiter.consume(tokens):
                raise RateLimitExceededError(f"Rate limit exceeded for {limiter_name}")

            return True

    def check_sliding_window_limit(self, limiter_name: str, key: str) -> bool:
        """
        Check if a request is allowed by a sliding window limiter.

        Args:
            limiter_name: Name of the rate limiter
            key: Identifier for the client/resource being rate limited

        Returns:
            True if request is allowed, False if rate limit would be exceeded

        Raises:
            RateLimitExceededError: If rate limit is exceeded
        """
        with self.lock:
            if limiter_name not in self.window_limiters:
                # No limiter configured, allow the request
                return True

            limiter = self.window_limiters[limiter_name]
            if not limiter.is_allowed(key):
                raise RateLimitExceededError(f"Rate limit exceeded for {limiter_name}")

            return True


# Global rate limiter manager instance
_rate_limiter_manager: Optional[RateLimiterManager] = None


def get_rate_limiter_manager() -> RateLimiterManager:
    """
    Get the global rate limiter manager instance.

    Returns:
        RateLimiterManager instance
    """
    global _rate_limiter_manager
    if _rate_limiter_manager is None:
        _rate_limiter_manager = RateLimiterManager()
    return _rate_limiter_manager


def rate_limit_by_token_bucket(limiter_name: str, tokens: int = 1):
    """
    Decorator to apply token bucket rate limiting to a function.

    Args:
        limiter_name: Name of the rate limiter to use
        tokens: Number of tokens to consume per call
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            rate_limiter_manager = get_rate_limiter_manager()
            rate_limiter_manager.check_token_bucket_limit(limiter_name, tokens)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit_by_sliding_window(limiter_name: str, key_func=None):
    """
    Decorator to apply sliding window rate limiting to a function.

    Args:
        limiter_name: Name of the rate limiter to use
        key_func: Function to generate the key from function arguments
                 If None, uses the first argument as the key
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate key
            if key_func:
                key = key_func(*args, **kwargs)
            elif args:
                key = str(args[0])
            else:
                key = "default"

            rate_limiter_manager = get_rate_limiter_manager()
            rate_limiter_manager.check_sliding_window_limit(limiter_name, key)
            return func(*args, **kwargs)
        return wrapper
    return decorator