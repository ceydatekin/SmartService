import pytest
from src.domain.rules import BusinessRuleValidationError


async def test_create_model_service(model_service, sample_model_data):
    """Test model creation through service"""
    model = await model_service.create_model(
        sample_model_data,
        user_id="test_user"
    )

    assert model.name == sample_model_data["name"]
    assert model.type == sample_model_data["type"]
    assert model.configuration == sample_model_data["configuration"]


async def test_model_validation(model_service):
    """Test model validation rules"""
    invalid_data = {
        "name": "Test",  # Missing required fields
    }

    with pytest.raises(BusinessRuleValidationError):
        await model_service.create_model(invalid_data, user_id="test_user")


async def test_feature_addition(model_service, feature_service, sample_model_data, sample_feature_data):
    """Test feature addition to model"""
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


@pytest.mark.integration
async def test_orchestrator_flow(orchestrator, sample_model_data):
    """Test complete orchestration flow"""
    result = await orchestrator.provision_model(
        sample_model_data,
        user_id="test_user"
    )

    assert result["model"] is not None
    assert result["integrations"] is not None
    assert result["model"].name == sample_model_data["name"]