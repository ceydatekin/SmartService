import os
import sys
import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import grpc
from concurrent import futures

# Absolute imports
from src.models.models import Base
from src.services.model_service import ModelService
from src.services.feature_service import FeatureService
from src.integrations.manager import IntegrationManager
from src.orchestration.orchestration import ModelOrchestrator
from src import smart_service_pb2 as pb2
from src import smart_service_pb2_grpc
from src.services.service import SmartServiceServicer
from src.utils.cache import Cache
from src.utils.monitoring import MetricsServer

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    try:
        DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/smartdb')
        engine = create_engine(DB_URL)
        Base.metadata.create_all(engine)
        return sessionmaker(bind=engine)
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def init_services(session_maker):
    try:
        cache = Cache()

        model_service = ModelService(session_maker(), cache)
        feature_service = FeatureService(session_maker(), cache)

        integration_manager = IntegrationManager()

        orchestrator = ModelOrchestrator(
            model_service=model_service,
            feature_service=feature_service,
            integration_manager=integration_manager
        )

        return model_service, feature_service, integration_manager, orchestrator
    except Exception as e:
        logger.error(f"Service initialization failed: {str(e)}")
        raise


class GRPCServiceHandler(smart_service_pb2_grpc.SmartServiceServicer):
    def __init__(self, model_service, feature_service, orchestrator):
        self.model_service = model_service
        self.feature_service = feature_service
        self.orchestrator = orchestrator

    async def CreateModel(self, request, context):
        try:
            result = await self.model_service.create_model(
                {
                    'name': request.name,
                    'type': request.type,
                    'category': request.category,
                    'description': request.description,
                    'configuration': request.configuration,
                },
                request.user_id
            )
            return pb2.SmartModel(
                id=str(result.id),
                name=result.name,
                type=result.type,
                category=result.category,
                description=result.description
            )
        except Exception as e:
            logger.error(f"CreateModel failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SmartModel()


async def serve():
    try:
        session_maker = init_db()
        model_service, feature_service, integration_manager, orchestrator = init_services(session_maker)

        metrics_server = MetricsServer()
        metrics_server.start(port=8000)

        server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=10),
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024)
            ]
        )

        service = GRPCServiceHandler(
            model_service=model_service,
            feature_service=feature_service,
            orchestrator=orchestrator
        )
        smart_service_pb2_grpc.add_SmartServiceServicer_to_server(service, server)

        port = os.getenv('GRPC_PORT', '50051')
        server.add_insecure_port(f'[::]:{port}')
        await server.start()
        logger.info(f"Server started on port {port}")

        await server.wait_for_termination()

    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        sys.exit(1)


async def serve():
    try:
        session_maker = init_db()
        model_service, feature_service, integration_manager, orchestrator = init_services(session_maker)

        metrics_server = MetricsServer()
        metrics_server.start(port=8000)

        server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=10),
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024)
            ]
        )

        service = SmartServiceServicer(
            model_service=model_service,
            feature_service=feature_service,
            orchestrator=orchestrator
        )
        smart_service_pb2_grpc.add_SmartServiceServicer_to_server(service, server)

        port = os.getenv('GRPC_PORT', '50051')
        server.add_insecure_port(f'[::]:{port}')
        await server.start()
        logger.info(f"Server started on port {port}")

        await server.wait_for_termination()

    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(serve())