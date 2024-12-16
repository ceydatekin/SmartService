import asyncio
from typing import Dict, Any, List
import logging
from datetime import datetime
from ..services.model_service import ModelService
from ..services.feature_service import FeatureService
from ..integrations.manager import IntegrationManager
from ..domain.events import ModelCreated, FeatureAdded
from ..utils.monitoring import monitor

logger = logging.getLogger(__name__)


class ModelOrchestrator:
    """Model ve feature'ların yaşam döngüsünü yöneten orchestrator"""

    def __init__(
            self,
            model_service: ModelService,
            feature_service: FeatureService,
            integration_manager: IntegrationManager
    ):
        self.model_service = model_service
        self.feature_service = feature_service
        self.integration_manager = integration_manager

    @monitor("provision_model")
    async def provision_model(
            self,
            model_data: Dict[str, Any],
            user_id: str
    ) -> Dict[str, Any]:
        """Yeni model oluşturma ve konfigürasyon süreci"""
        try:
            # Model oluştur
            model = self.model_service.create_model(model_data, user_id)

            # Entegrasyonları kur
            integration_results = await self._setup_integrations(
                model.id,
                model_data.get('integrations', [])
            )

            # Feature'ları ekle
            feature_results = await self._add_features(
                model.id,
                model_data.get('features', []),
                user_id
            )

            return {
                "model": model,
                "integrations": integration_results,
                "features": feature_results
            }

        except Exception as e:
            logger.error(f"Model provision failed: {str(e)}")
            # Cleanup işlemleri
            await self._cleanup_failed_provision(model.id)
            raise

    async def _setup_integrations(
            self,
            model_id: str,
            integrations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Model entegrasyonlarını kurma"""
        results = {}
        for integration_config in integrations:
            try:
                success = await self.integration_manager.setup_integration(
                    integration_config
                )
                results[integration_config['type']] = {
                    "status": "SUCCESS" if success else "FAILED"
                }
            except Exception as e:
                results[integration_config['type']] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        return results

    async def _add_features(
            self,
            model_id: str,
            features: List[Dict[str, Any]],
            user_id: str
    ) -> Dict[str, Any]:
        """Model feature'larını ekleme"""
        results = {}
        for feature_data in features:
            try:
                feature = await self.feature_service.add_feature(
                    model_id,
                    feature_data,
                    user_id
                )
                results[feature.name] = {
                    "status": "SUCCESS",
                    "id": feature.id
                }
            except Exception as e:
                results[feature_data['name']] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        return results

    @monitor("model_update")
    async def update_model_configuration(
            self,
            model_id: str,
            config_updates: Dict[str, Any],
            user_id: str
    ) -> Dict[str, Any]:
        """Model konfigürasyonunu güncelleme"""
        try:
            # Mevcut entegrasyonları kontrol et
            health_status = await self.integration_manager.health_check_all()

            # Model güncelle
            updated_model = self.model_service.update_model(
                model_id,
                config_updates,
                user_id
            )

            # Entegrasyonları yeniden konfigüre et
            if 'integrations' in config_updates:
                await self._reconfigure_integrations(
                    model_id,
                    config_updates['integrations']
                )

            return {
                "model": updated_model,
                "health_status": health_status
            }

        except Exception as e:
            logger.error(f"Model update failed: {str(e)}")
            raise

    async def _cleanup_failed_provision(self, model_id: str):
        """Başarısız provision temizleme"""
        try:
            # Entegrasyonları temizle
            await self.integration_manager.cleanup()

            # Model ve feature'ları temizle
            self.model_service.delete_model(model_id)

        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

    @monitor("model_status_check")
    async def check_model_status(self, model_id: str) -> Dict[str, Any]:
        """Model ve bağlı sistemlerin durumunu kontrol et"""
        try:
            model = self.model_service.get_model(model_id)
            if not model:
                raise ValueError(f"Model not found: {model_id}")

            # Integration sağlık kontrolü
            integration_status = await self.integration_manager.health_check_all()

            # Feature durumlarını kontrol et
            feature_status = {}
            for feature in model.features:
                feature_status[feature.id] = {
                    "status": feature.status,
                    "last_updated": feature.updated_at
                }

            return {
                "model_status": model.status,
                "integrations": integration_status,
                "features": feature_status,
                "last_checked": datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            raise