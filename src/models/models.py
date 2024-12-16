from sqlalchemy import Column, String, JSON, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import uuid

Base = declarative_base()


class ModelCategory(enum.Enum):
    WEARABLE = "wearable"
    SURVEILLANCE = "surveillance"
    ENVIRONMENTAL = "environmental"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    WEATHER = "weather"
    CUSTOM = "custom"


class DeviceProtocol(enum.Enum):
    MQTT = "mqtt"
    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    BLUETOOTH = "bluetooth"
    CUSTOM = "custom"


class SmartModel(Base):
    __tablename__ = "smart_models"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    category = Column(Enum(ModelCategory), nullable=False)
    description = Column(Text)
    version = Column(String(50), nullable=False)

    metadata = Column(JSON)
    configuration = Column(JSON)
    capabilities = Column(JSON)

    protocol = Column(Enum(DeviceProtocol), nullable=True)
    connection_info = Column(JSON, nullable=True)
    requires_authentication = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    features = relationship("SmartFeature", back_populates="model", cascade="all, delete-orphan")
    integrations = relationship("ModelIntegration", back_populates="model")


class FeatureType(enum.Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    ANALYTICS = "analytics"
    CONTROL = "control"
    DATA_PROCESSING = "data_processing"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"
    CUSTOM = "custom"


class SmartFeature(Base):
    __tablename__ = "smart_features"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(36), ForeignKey('smart_models.id'), nullable=False)
    name = Column(String(255), nullable=False)
    feature_type = Column(Enum(FeatureType), nullable=False)
    description = Column(Text)

    parameters = Column(JSON)
    response_format = Column(JSON)
    constraints = Column(JSON)
    dependencies = Column(JSON)

    endpoint = Column(String(255), nullable=True)
    method = Column(String(50), nullable=True)
    rate_limit = Column(JSON, nullable=True)

    is_active = Column(Boolean, default=True)
    requires_auth = Column(Boolean, default=False)
    status = Column(String(50), default='ACTIVE')

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    model = relationship("SmartModel", back_populates="features")
    validations = relationship("FeatureValidation", back_populates="feature")


class ModelIntegration(Base):
    __tablename__ = "model_integrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(36), ForeignKey('smart_models.id'), nullable=False)
    name = Column(String(255), nullable=False)
    integration_type = Column(String(50), nullable=False)
    config = Column(JSON)
    status = Column(String(50), default='ACTIVE')

    model = relationship("SmartModel", back_populates="integrations")


class FeatureValidation(Base):
    __tablename__ = "feature_validations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    feature_id = Column(String(36), ForeignKey('smart_features.id'), nullable=False)
    validation_type = Column(String(50), nullable=False)
    rules = Column(JSON)
    is_required = Column(Boolean, default=True)

    feature = relationship("SmartFeature", back_populates="validations")