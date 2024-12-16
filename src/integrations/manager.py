from typing import Dict, Any, List
import asyncio
from .integration import IntegrationFactory
from ..models.models import ModelIntegration
from ..utils.monitoring import monitor


class IntegrationManager:
    """Integration yönetim sınıfı"""

    def __init__(self):
        self.active_integrations: Dict[str, BaseIntegration] = {}

    @monitor("setup_integration")
    async def setup_integration(self, integration_config: ModelIntegration) -> bool:
        """Yeni bir entegrasyon kur"""
        try:
            integration = IntegrationFactory.create(
                integration_config.integration_type,
                integration_config.config
            )

            # Bağlantıyı test et
            if await integration.connect():
                self.active_integrations[integration_config.id] = integration
                return True
            return False

        except Exception as e:
            logger.error(f"Integration setup error: {str(e)}")
            return False

    @monitor("execute_integration")
    async def execute_integration(
            self,
            integration_id: str,
            action: str,
            params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Entegrasyon aksiyonu çalıştır"""
        if integration_id not in self.active_integrations:
            raise ValueError(f"Integration not found: {integration_id}")

        integration = self.active_integrations[integration_id]
        return await integration.execute(action, params)

    async def health_check_all(self) -> Dict[str, bool]:
        """Tüm entegrasyonların sağlık kontrolü"""
        health_status = {}
        for int_id, integration in self.active_integrations.items():
            health_status[int_id] = await integration.health_check()
        return health_status

    async def cleanup(self):
        """Tüm aktif entegrasyonları temizle"""
        self.active_integrations.clear()