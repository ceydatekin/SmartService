import aiohttp
import logging
from typing import Dict, Any
from ..utils.resilience import CircuitBreaker, RateLimiter, Retry

logger = logging.getLogger(__name__)


class BaseIntegration:
    """Base integration class"""

    def __init__(self, config: Dict[str, Any]):
        self.config = self._validate_config(config)
        self.status = "INITIALIZED"

    async def connect(self) -> bool:
        """Base connect method"""
        raise NotImplementedError

    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Base execute method"""
        raise NotImplementedError

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration"""
        required_fields = ['base_url', 'auth_type']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required config field: {field}")
        return config


class IoTDeviceIntegration(BaseIntegration):
    @CircuitBreaker(failure_threshold=3, reset_timeout=60)
    @RateLimiter(max_requests=100, time_window=60)
    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config['base_url']}/connect"
                headers = self._get_auth_headers()

                async with session.post(url, headers=headers) as response:
                    return response.status == 200

        except Exception as e:
            logger.error(f"IoT device connection error: {str(e)}")
            return False

    @CircuitBreaker(failure_threshold=3, reset_timeout=60)
    @RateLimiter(max_requests=100, time_window=60)
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config['base_url']}/{action}"
                headers = self._get_auth_headers()

                async with session.post(url, json=params, headers=headers) as response:
                    return await response.json()

        except Exception as e:
            logger.error(f"IoT device execution error: {str(e)}")
            raise

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on config"""
        if self.config['auth_type'] == 'bearer':
            return {'Authorization': f"Bearer {self.config['auth_token']}"}
        elif self.config['auth_type'] == 'api_key':
            return {'X-API-Key': self.config['api_key']}
        return {}


class WeatherServiceIntegration(BaseIntegration):
    @CircuitBreaker(failure_threshold=3, reset_timeout=60)
    async def connect(self) -> bool:
        return True  # API key validation yeterli

    @CircuitBreaker(failure_threshold=3, reset_timeout=60)
    @RateLimiter(max_requests=50, time_window=60)
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config['base_url']}/{action}"
                params['apikey'] = self.config['api_key']

                async with session.get(url, params=params) as response:
                    return await response.json()

        except Exception as e:
            logger.error(f"Weather service execution error: {str(e)}")
            raise


class IntegrationFactory:
    _integrations = {
        'iot_device': IoTDeviceIntegration,
        'weather': WeatherServiceIntegration
    }

    @classmethod
    def create(cls, integration_type: str, config: Dict[str, Any]) -> BaseIntegration:
        if integration_type not in cls._integrations:
            raise ValueError(f"Unknown integration type: {integration_type}")
        return cls._integrations[integration_type](config)

    @classmethod
    def register_integration(cls, name: str, integration_class: type):
        if not issubclass(integration_class, BaseIntegration):
            raise ValueError("Integration must inherit from BaseIntegration")
        cls._integrations[name] = integration_class