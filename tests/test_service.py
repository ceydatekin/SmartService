import pytest
from src.domain.rules import BusinessRuleValidationError
from src.models.models import ModelType


@pytest.mark.asyncio
async def test_create_model_service(model_service, sample_model_data):
    """Test model creation through service"""
    # Ensure type is ModelType enum
    sample_model_data['type'] = ModelType.DEVICE

    model = await model_service.create_model(
        sample_model_data,
        user_id="test_user"
    )

    assert model.name == sample_model_data["name"]
    assert model.type == sample_model_data["type"]
    assert model.configuration == sample_model_data["configuration"]


@pytest.mark.asyncio
async def test_model_validation(model_service):
    """Test model validation rules"""
    invalid_data = {
        "name": "Test",  # Missing type field
    }

    with pytest.raises(BusinessRuleValidationError) as exc:
        await model_service.create_model(invalid_data, user_id="test_user")
    assert "Missing required fields: type" in str(exc.value)  # field -> fields olarak düzeltildi


@pytest.mark.asyncio
async def test_feature_addition(model_service, feature_service, sample_model_data, sample_feature_data):
    """Test feature addition to model"""
    # Ensure type is ModelType enum
    sample_model_data['type'] = ModelType.DEVICE

    model = await model_service.create_model(
        sample_model_data,
        user_id="test_user"
    )

    feature = await feature_service.add_feature(
        model.id,
        sample_feature_data,
        user_id="test_user"
    )

    assert feature.model_id == model.id
    assert feature.name == sample_feature_data["name"]