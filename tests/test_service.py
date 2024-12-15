import pytest
from unittest.mock import MagicMock
from src.services.service import SmartServiceServicer
from src import smart_service_pb2 as pb2


@pytest.fixture
def service():
    session_maker = MagicMock()
    session_maker.return_value.__enter__ = MagicMock(return_value=MagicMock())
    session_maker.return_value.__exit__ = MagicMock(return_value=None)
    return SmartServiceServicer(session_maker)


def test_create_model(service):
    # Test verisi
    request = MagicMock()
    request.model = pb2.SmartModel(
        name="Test Camera",
        type="DEVICE",
        category="camera",
        description="Test description"
    )

    context = MagicMock()

    # Test
    response = service.CreateModel(request, context)

    # Assertion
    assert response.name == "Test Camera"
    assert response.type == "DEVICE"



