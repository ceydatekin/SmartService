import pytest
from src.models.models import SmartModel, SmartFeature, ModelStatus
from datetime import datetime


def test_create_smart_model(db_session, sample_model_data):
    """Test model creation"""
    model = SmartModel(
        name=sample_model_data["name"],
        type=sample_model_data["type"],
        category=sample_model_data["category"],
        description=sample_model_data["description"],
        configuration=sample_model_data["configuration"]
    )

    db_session.add(model)
    db_session.commit()

    assert model.id is not None
    assert model.name == sample_model_data["name"]
    assert model.status == ModelStatus.DRAFT
    assert isinstance(model.created_at, datetime)


def test_add_feature_to_model(db_session, sample_model_data, sample_feature_data):
    """Test adding feature to model"""
    model = SmartModel(**sample_model_data)
    db_session.add(model)
    db_session.commit()

    feature = SmartFeature(
        model_id=model.id,
        **sample_feature_data
    )

    model.features.append(feature)
    db_session.commit()

    assert len(model.features) == 1
    assert model.features[0].name == sample_feature_data["name"]


def test_model_status_transitions(db_session, sample_model_data):
    """Test model status transitions"""
    model = SmartModel(**sample_model_data)

    assert model.status == ModelStatus.DRAFT

    model.status = ModelStatus.ACTIVE
    assert model.status == ModelStatus.ACTIVE

    # Should not allow invalid status transitions
    with pytest.raises(ValueError):
        model.status = "INVALID_STATUS"