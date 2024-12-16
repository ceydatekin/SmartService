import time
from functools import wraps
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)


class CircuitBreakerState:
    CLOSED = "CLOSED"  # Normal çalışma durumu
    OPEN = "OPEN"  # Hata durumu - istekler engelleniyor
    HALF_OPEN = "HALF_OPEN"  # Test durumu


class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            await self._before_call()
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                await self._on_failure(e)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            self._before_call()
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure(e)
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    def _before_call(self):
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

    def _on_success(self):
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.failures = 0
            self.last_failure_time = None

    async def _on_failure(self, exception):
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failures} failures")

    def _should_attempt_reset(self):
        if not self.last_failure_time:
            return True
        return (datetime.now() - self.last_failure_time).seconds >= self.reset_timeout


class RateLimiter:
    def __init__(self, max_requests=100, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            self._check_limit()
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            self._check_limit()
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    def _check_limit(self):
        now = datetime.now()
        # Eski istekleri temizle
        self.requests = [req for req in self.requests
                         if (now - req) < timedelta(seconds=self.time_window)]

        # Rate limit kontrolü
        if len(self.requests) >= self.max_requests:
            raise Exception(f"Rate limit exceeded: {self.max_requests} requests per {self.time_window}s")

        self.requests.append(now)


class Retry:
    def __init__(self, max_retries=3, delay=1, backoff=2):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            delay = self.delay

            for attempt in range(self.max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(delay)
                        delay *= self.backoff

            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            delay = self.delay

            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(delay)
                        delay *= self.backoff

            raise last_exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper