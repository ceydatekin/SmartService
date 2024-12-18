import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock

from src.models.models import Base, ModelType, FeatureType
from src.services.model_service import ModelService
from src.services.feature_service import FeatureService
from src.orchestration.orchestration import ModelOrchestrator
from src.integrations.manager import IntegrationManager
from src.utils.cache import Cache

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def engine():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def mock_cache():
    cache = MagicMock(spec=Cache)
    cache.get.return_value = None
    return cache

@pytest.fixture
def model_service(db_session, mock_cache):
    return ModelService(db_session, mock_cache)

@pytest.fixture
def feature_service(db_session, mock_cache):
    return FeatureService(db_session, mock_cache)

@pytest.fixture
def mock_integration_manager():
    manager = MagicMock(spec=IntegrationManager)
    manager.setup_integration.return_value = True
    manager.health_check_all.return_value = {"test_integration": "healthy"}
    return manager

@pytest.fixture
def orchestrator(model_service, feature_service, mock_integration_manager):
    return ModelOrchestrator(
        model_service=model_service,
        feature_service=feature_service,
        integration_manager=mock_integration_manager
    )

@pytest.fixture
def sample_model_data():
    return {
        "name": "Test Camera",
        "type": ModelType.DEVICE,
        "category": "surveillance",
        "vendor": "Test Corp",
        "description": "Test camera description",
        "configuration": {
            "settings": {"resolution": "1080p"}
        },
        "capabilities": ["night_vision", "motion_detection"]
    }

@pytest.fixture
def sample_feature_data():
    return {
        "name": "Take Photo",
        "feature_type": FeatureType.SENSOR,
        "description": "Takes a photo",
        "parameters": {
            "resolution": "string",
            "format": "string"
        },
        "response_schema": {
            "image_url": "string",
            "timestamp": "datetime"
        }
    }