import pytest
from unittest.mock import patch
from src.integrations.integration import IoTDeviceIntegration, WeatherServiceIntegration


@pytest.fixture
def sample_integration_config():
    return {
        "base_url": "http://test-api.com",
        "auth_type": "bearer",
        "settings": {
            "token": "test-token"
        }
    }


@pytest.mark.integration
async def test_iot_device_integration(sample_integration_config):
    """Test IoT device integration"""
    integration = IoTDeviceIntegration(sample_integration_config)

    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json.return_value = {
            "status": "success"
        }

        connected = await integration.connect()
        assert connected

        result = await integration.execute(
            "take_photo",
            {"resolution": "1080p"}
        )
        assert result["status"] == "success"


@pytest.mark.integration
async def test_integration_retry_mechanism(sample_integration_config):
    """Test integration retry mechanism"""
    integration = IoTDeviceIntegration(sample_integration_config)

    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.side_effect = [
            Exception("Connection failed"),
            Exception("Still failed"),
            {"status": "success"}
        ]

        result = await integration.retry_with_backoff(
            integration.execute,
            "test_action",
            {}
        )
        assert result["status"] == "success"