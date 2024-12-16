import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import grpc
from unittest.mock import MagicMock

from src.models.models import Base
from src.services.model_service import ModelService
from src.services.feature_service import FeatureService
from src.integrations.manager import IntegrationManager
from src.orchestration.orchestration import ModelOrchestrator
from src.utils.cache import Cache

@pytest.fixture
def engine():
    """Test database engine"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(engine):
    """Database session for tests"""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def mock_cache():
    """Mock cache instance"""
    cache = MagicMock(spec=Cache)
    cache.get.return_value = None
    return cache

@pytest.fixture
def model_service(db_session, mock_cache):
    """Model service instance"""
    return ModelService(db_session, mock_cache)

@pytest.fixture
def feature_service(db_session, mock_cache):
    """Feature service instance"""
    return FeatureService(db_session, mock_cache)

@pytest.fixture
def mock_integration_manager():
    """Mock integration manager"""
    manager = MagicMock(spec=IntegrationManager)
    manager.setup_integration.return_value = True
    manager.health_check_all.return_value = {"test_integration": "healthy"}
    return manager

@pytest.fixture
def orchestrator(model_service, feature_service, mock_integration_manager):
    """Orchestrator instance"""
    return ModelOrchestrator(
        model_service=model_service,
        feature_service=feature_service,
        integration_manager=mock_integration_manager
    )

@pytest.fixture
def sample_model_data():
    """Sample model data for tests"""
    return {
        "name": "Test Camera",
        "type": "DEVICE",
        "category": "surveillance",
        "description": "Test camera description",
        "version": "1.0",
        "meta_info": {"manufacturer": "Test Corp", "model": "TC-100"},
        "configuration": {
            "settings": {"resolution": "1080p"},
            "capabilities": ["night_vision", "motion_detection"]
        }
    }

@pytest.fixture
def sample_feature_data():
    """Sample feature data for tests"""
    return {
        "name": "Take Photo",
        "feature_type": "capture",
        "parameters": {
            "resolution": "string",
            "format": "string"
        },
        "response_schema": {
            "image_url": "string",
            "timestamp": "datetime"
        }
    }