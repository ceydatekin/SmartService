from abc import ABC, abstractmethod
from typing import Dict, Any
from ..utils.resilience import CircuitBreaker, RateLimiter

class BaseIntegration(ABC):
    """Base integration class for all external integrations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter()

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