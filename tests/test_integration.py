import pytest
from unittest.mock import patch, AsyncMock
from src.integrations.integration import IoTDeviceIntegration, WeatherServiceIntegration, IntegrationFactory


@pytest.fixture
def sample_iot_config():
    return {
        "base_url": "http://test-api.com",
        "auth_type": "bearer",
        "auth_token": "test-token"
    }


@pytest.fixture
def sample_weather_config():
    return {
        "base_url": "http://weather-api.com",
        "auth_type": "api_key",
        "api_key": "test-key"
    }


@pytest.mark.asyncio
async def test_iot_device_integration(sample_iot_config):
    """Test IoT device integration"""
    integration = IoTDeviceIntegration(sample_iot_config)

    # Mock aiohttp ClientSession
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"status": "success"}

    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response

        # Test connection
        connected = await integration.connect()
        assert connected is True

        # Test execution
        result = await integration.execute(
            "take_photo",
            {"resolution": "1080p"}
        )
        assert result["status"] == "success"


@pytest.mark.asyncio
async def test_weather_service_integration(sample_weather_config):
    """Test weather service integration"""
    integration = WeatherServiceIntegration(sample_weather_config)

    mock_response = AsyncMock()
    mock_response.json.return_value = {"temperature": 20}

    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        # Test execution
        result = await integration.execute(
            "current",
            {"city": "London"}
        )
        assert "temperature" in result


@pytest.mark.asyncio
async def test_integration_factory():
    """Test integration factory"""
    config = {
        "base_url": "http://test-api.com",
        "auth_type": "bearer",
        "auth_token": "test-token"
    }

    # Create IoT integration
    iot_integration = IntegrationFactory.create("iot_device", config)
    assert isinstance(iot_integration, IoTDeviceIntegration)

    # Test invalid type
    with pytest.raises(ValueError):
        IntegrationFactory.create("invalid_type", config)