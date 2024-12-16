import os
import sys
import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import grpc
from concurrent import futures

from models.models import Base
from services.model_service import ModelService
from services.feature_service import FeatureService
from integrations.manager import IntegrationManager
from orchestration.orchestration import ModelOrchestrator
from src.smart_service_pb2_grpc import SmartServiceServicer, add_SmartServiceServicer_to_server
from utils.cache import Cache
from utils.monitoring import MetricsServer

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize database connection"""
    try:
        DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/smartdb')
        engine = create_engine(DB_URL)
        Base.metadata.create_all(engine)
        return sessionmaker(bind=engine)
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def init_services(session_maker):
    """Initialize all services"""
    try:
        # Initialize cache
        cache = Cache()

        # Initialize services
        model_service = ModelService(session_maker(), cache)
        feature_service = FeatureService(session_maker(), cache)

        # Initialize integration manager
        integration_manager = IntegrationManager()

        # Initialize orchestrator
        orchestrator = ModelOrchestrator(
            model_service=model_service,
            feature_service=feature_service,
            integration_manager=integration_manager
        )

        return model_service, feature_service, integration_manager, orchestrator
    except Exception as e:
        logger.error(f"Service initialization failed: {str(e)}")
        raise


async def serve():
    """Start gRPC server"""
    try:
        # Initialize services
        session_maker = init_db()
        model_service, feature_service, integration_manager, orchestrator = init_services(session_maker)

        # Start metrics server
        metrics_server = MetricsServer()
        metrics_server.start(port=8000)

        # Create gRPC server
        server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=10),
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024)
            ]
        )

        # Add servicer to server
        service = SmartServiceServicer(
            model_service=model_service,
            feature_service=feature_service,
            orchestrator=orchestrator
        )
        add_SmartServiceServicer_to_server(service, server)

        # Start serving
        port = os.getenv('GRPC_PORT', '50051')
        server.add_insecure_port(f'[::]:{port}')
        await server.start()
        logger.info(f"Server started on port {port}")

        # Keep alive
        await server.wait_for_termination()

    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(serve())