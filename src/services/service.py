import grpc
from typing import Dict, Any
import logging

from src import smart_service_pb2 as pb2
from src import smart_service_pb2_grpc as pb2_grpc
from src.utils.monitoring import monitor

logger = logging.getLogger(__name__)

class SmartServiceServicer(pb2_grpc.SmartServiceServicer):
    def __init__(self, model_service=None, feature_service=None, orchestrator=None):
        self.model_service = model_service
        self.feature_service = feature_service
        self.orchestrator = orchestrator

    @monitor("grpc_create_model")
    async def CreateModel(self, request, context):
        try:
            result = await self.orchestrator.provision_model(
                {
                    'name': request.name,
                    'type': request.type,
                    'category': request.category,
                    'description': request.description,
                    'configuration': self._convert_config(request.configuration),
                    'integrations': list(request.integrations),
                    'features': list(request.features)
                },
                request.user_id
            )
            return self._convert_to_proto_model(result['model'])
        except Exception as e:
            logger.error(f"CreateModel failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SmartModel()

    @monitor("grpc_get_model_status")
    async def GetModelStatus(self, request, context):
        try:
            status = await self.orchestrator.check_model_status(request.model_id)
            return pb2.ModelStatusResponse(
                model_id=request.model_id,
                status=status['model_status'],
                integration_status=status['integrations'],
                feature_status=status['features'],
                last_checked=status['last_checked'].isoformat()
            )
        except Exception as e:
            logger.error(f"GetModelStatus failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.ModelStatusResponse()

    def _convert_to_proto_model(self, model: Dict[str, Any]) -> pb2.SmartModel:
        """Convert model dictionary to proto message"""
        return pb2.SmartModel(
            id=model['id'],
            name=model['name'],
            type=model['type'],
            category=model['category'],
            description=model['description'],
            status=model['status'],
            version=model['version'],
            configuration=self._convert_config(model['configuration']),
            features=[self._convert_to_proto_feature(f) for f in model['features']],
            integrations=[self._convert_to_proto_integration(i) for i in model['integrations']],
            created_by=model['created_by'],
            created_at=model['created_at'].isoformat(),
            updated_at=model['updated_at'].isoformat()
        )

    def _convert_config(self, config) -> pb2.ModelConfiguration:
        """Convert configuration dictionary to proto message"""
        if not config:
            return pb2.ModelConfiguration()
        return pb2.ModelConfiguration(
            settings=config.get('settings', {}),
            capabilities=config.get('capabilities', []),
            metadata=config.get('metadata', {})
        )