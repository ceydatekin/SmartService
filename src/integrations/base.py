from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import logging
from ..utils.resilience import CircuitBreaker, RateLimiter
from ..utils.monitoring import monitor

logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Base exception for integration errors"""
    pass


class ConnectionError(IntegrationError):
    """Raised when connection fails"""
    pass


class ExecutionError(IntegrationError):
    """Raised when execution fails"""
    pass


class BaseIntegration(ABC):
    """Base integration class for all external integrations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = self._validate_config(config)
        self.status = "INITIALIZED"
        self.last_connection = None
        self.connection_attempts = 0
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 5)
        self.timeout = config.get('timeout', 30)

        # Circuit breaker ve rate limiter
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.get('failure_threshold', 5),
            reset_timeout=config.get('reset_timeout', 60)
        )
        self.rate_limiter = RateLimiter(
            max_requests=config.get('max_requests', 100),
            time_window=config.get('time_window', 60)
        )

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Config validation"""
        required_fields = ['base_url', 'auth_type']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required config field: {field}")
        return config

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection with external service"""
        pass

    @abstractmethod
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration action"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check integration health status"""
        pass

    @monitor("integration_retry")
    async def retry_with_backoff(self, operation, *args, **kwargs) -> Any:
        """Exponential backoff retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = (2 ** attempt) * self.retry_delay
                logger.warning(
                    f"Operation failed, retrying in {wait_time}s. "
                    f"Error: {str(e)}"
                )
                await asyncio.sleep(wait_time)

    async def disconnect(self) -> bool:
        """Clean disconnection from service"""
        try:
            self.status = "DISCONNECTED"
            self.last_connection = None
            return True
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return {
            "status": self.status,
            "last_connection": self.last_connection,
            "connection_attempts": self.connection_attempts,
            "circuit_breaker_status": self.circuit_breaker.state,
            "config": {
                k: v for k, v in self.config.items()
                if k not in ['api_key', 'secret']  # Hide sensitive data
            }
        }

    @monitor("integration_validate")
    async def validate_connection(self) -> bool:
        """Validate current connection"""
        try:
            if self.status != "CONNECTED":
                return False
            return await self.health_check()
        except Exception as e:
            logger.error(f"Connection validation error: {str(e)}")
            return False

    async def initialize(self) -> bool:
        """Initialize integration"""
        try:
            self.status = "INITIALIZING"
            if await self.connect():
                self.status = "CONNECTED"
                self.last_connection = datetime.utcnow()
                self.connection_attempts = 0
                return True
            return False
        except Exception as e:
            self.status = "ERROR"
            logger.error(f"Initialization error: {str(e)}")
            return False

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()