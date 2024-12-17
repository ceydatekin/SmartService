import asyncio
from functools import wraps
from datetime import datetime, timedelta
import logging
import time

logger = logging.getLogger(__name__)


class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            await self._check_state()
            try:
                result = await func(*args, **kwargs)
                await self._on_success()
                return result
            except Exception as e:
                await self._on_failure()
                raise e

        return async_wrapper

    async def _check_state(self):
        if self.state == "OPEN":
            if await self._should_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

    async def _on_success(self):
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failures = 0
            self.last_failure_time = None

    async def _on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"

    async def _should_reset(self):
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
        async def wrapper(*args, **kwargs):
            await self._check_limit()
            return await func(*args, **kwargs)

        return wrapper

    async def _check_limit(self):
        now = datetime.now()
        self.requests = [req for req in self.requests
                         if (now - req) < timedelta(seconds=self.time_window)]

        if len(self.requests) >= self.max_requests:
            raise Exception(f"Rate limit exceeded: {self.max_requests} requests per {self.time_window}s")

        self.requests.append(now)


class Retry:
    def __init__(self, max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            delay = self.delay

            for attempt in range(self.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_attempts} failed: {str(e)}"
                    )

                    if attempt + 1 < self.max_attempts:
                        await asyncio.sleep(delay)
                        delay *= self.backoff

            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            delay = self.delay

            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_attempts} failed: {str(e)}"
                    )

                    if attempt + 1 < self.max_attempts:
                        time.sleep(delay)
                        delay *= self.backoff

            raise last_exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper