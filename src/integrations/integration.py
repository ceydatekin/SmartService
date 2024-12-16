import aiohttp
import asyncio
from typing import Dict, Any
import json
import logging
from .base import BaseIntegration
from ..utils.monitoring import monitor
from ..utils.resilience import CircuitBreaker, RateLimiter, Retry

logger = logging.getLogger(__name__)


class IoTDeviceIntegration(BaseIntegration):
    """IoT cihazları için entegrasyon"""

    @monitor("iot_connect")
    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config['base_url']}/device/{self.config['device_id']}/connect"
                async with session.post(url, json=self.config['auth']) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"IoT connection error: {str(e)}")
            return False

    @monitor("iot_execute")
    @CircuitBreaker(failure_threshold=3, reset_timeout=60)
    @RateLimiter(max_requests=100, time_window=60)
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.config['base_url']}/device/{self.config['device_id']}/{action}"
            async with session.post(url, json=params) as response:
                return await response.json()

    async def health_check(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config['base_url']}/device/{self.config['device_id']}/status"
                async with session.get(url) as response:
                    return response.status == 200
        except:
            return False


class WeatherServiceIntegration(BaseIntegration):
    """Hava durumu servisi entegrasyonu"""

    @monitor("weather_connect")
    async def connect(self) -> bool:
        # API key validation
        return bool(self.config.get('api_key'))

    @monitor("weather_execute")
    @CircuitBreaker(failure_threshold=3, reset_timeout=60)
    @RateLimiter(max_requests=50, time_window=60)
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.config['base_url']}/{action}"
            params['apikey'] = self.config['api_key']
            async with session.get(url, params=params) as response:
                return await response.json()

    async def health_check(self) -> bool:
        return await self.execute('ping', {})


class IntegrationFactory:
    """Integration factory for creating appropriate integration instances"""

    _integrations = {
        'iot_device': IoTDeviceIntegration,
        'weather': WeatherServiceIntegration
    }

    @classmethod
    def create(cls, integration_type: str, config: Dict[str, Any]) -> BaseIntegration:
        if integration_type not in cls._integrations:
            raise ValueError(f"Unknown integration type: {integration_type}")

        integration_class = cls._integrations[integration_type]
        return integration_class(config)

    @classmethod
    def register_integration(cls, name: str, integration_class: type):
        """Register new integration type"""
        if not issubclass(integration_class, BaseIntegration):
            raise ValueError("Integration must inherit from BaseIntegration")

        cls._integrations[name] = integration_class