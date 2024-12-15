import pytest
from src.models.models import SmartModel, SmartFeature, ModelType, FeatureStatus


def test_smart_model_creation():
    model = SmartModel(
        name="Test Camera",
        type=ModelType.DEVICE,
        category="camera",
        description="Test description"
    )

    assert model.name == "Test Camera"
    assert model.type == ModelType.DEVICE
    assert model.category == "camera"
    assert model.features == []


def test_smart_feature_creation():
    feature = SmartFeature(
        model_id="test-id",
        name="Take Photo",
        description="Takes a photo",
        function_type="capture",
        status=FeatureStatus.ACTIVE
    )

    assert feature.name == "Take Photo"
    assert feature.function_type == "capture"
    assert feature.status == FeatureStatus.ACTIVE