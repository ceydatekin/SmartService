from sqlalchemy import (
    Column, String, JSON, DateTime, Text, ForeignKey,
    Enum, Boolean, Integer, Float, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum as PyEnum

Base = declarative_base()

# Many-to-Many tablolar
model_tags = Table('model_tags', Base.metadata,
                   Column('model_id', String(36), ForeignKey('smart_models.id')),
                   Column('tag_id', String(36), ForeignKey('tags.id'))
                   )

model_dependencies = Table('model_dependencies', Base.metadata,
                           Column('dependent_model_id', String(36), ForeignKey('smart_models.id')),
                           Column('dependency_model_id', String(36), ForeignKey('smart_models.id'))
                           )


# Enum sınıfları
class ModelType(PyEnum):
    DEVICE = "DEVICE"
    SERVICE = "SERVICE"
    GATEWAY = "GATEWAY"
    VIRTUAL = "VIRTUAL"
    COMPOSITE = "COMPOSITE"


class ModelStatus(PyEnum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    MAINTENANCE = "MAINTENANCE"


class SecurityLevel(PyEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FeatureType(PyEnum):
    SENSOR = "SENSOR"
    ACTUATOR = "ACTUATOR"
    ANALYTICS = "ANALYTICS"
    CONTROL = "CONTROL"


# Model sınıfları
class Tag(Base):
    __tablename__ = "tags"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False, unique=True)
    category = Column(String(50))
    description = Column(Text)


class SmartModel(Base):
    __tablename__ = "smart_models"

    # Ana alanlar
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(Enum(ModelType), nullable=False)
    status = Column(Enum(ModelStatus), default=ModelStatus.DRAFT)
    version = Column(String(50), nullable=False)
    revision = Column(Integer, default=1)

    # Sınıflandırma
    category = Column(String(100))
    vendor = Column(String(100))

    # Detaylar
    description = Column(Text)
    meta_info = Column(JSON)
    configuration = Column(JSON)
    capabilities = Column(JSON)

    # Güvenlik
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.MEDIUM)
    authentication_required = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    is_active = Column(Boolean, default=True)

    # İlişkiler
    features = relationship("SmartFeature", back_populates="model", cascade="all, delete-orphan")
    integrations = relationship("ModelIntegration", back_populates="model", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=model_tags, backref="models")

    def __init__(self, **kwargs):
        kwargs.setdefault('status', ModelStatus.DRAFT)
        kwargs.setdefault('security_level', SecurityLevel.MEDIUM)
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('version', "1.0")
        kwargs.setdefault('revision', 1)
        kwargs.setdefault('meta_info', {})
        kwargs.setdefault('configuration', {})
        kwargs.setdefault('capabilities', {})
        super(SmartModel, self).__init__(**kwargs)


class SmartFeature(Base):
    __tablename__ = "smart_features"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(36), ForeignKey('smart_models.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    feature_type = Column(Enum(FeatureType), nullable=False)

    parameters = Column(JSON)
    response_schema = Column(JSON)
    constraints = Column(JSON)

    is_active = Column(Boolean, default=True)
    requires_auth = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String(255))

    model = relationship("SmartModel", back_populates="features")

    def __init__(self, **kwargs):
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('requires_auth', False)
        kwargs.setdefault('parameters', {})
        kwargs.setdefault('response_schema', {})
        kwargs.setdefault('constraints', {})
        super(SmartFeature, self).__init__(**kwargs)


class ModelIntegration(Base):
    __tablename__ = "model_integrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(36), ForeignKey('smart_models.id'), nullable=False)
    name = Column(String(255), nullable=False)
    integration_type = Column(String(50), nullable=False)
    config = Column(JSON)
    status = Column(String(50), default='ACTIVE')

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    model = relationship("SmartModel", back_populates="integrations")

    def __init__(self, **kwargs):
        kwargs.setdefault('status', 'ACTIVE')
        kwargs.setdefault('config', {})
        super(ModelIntegration, self).__init__(**kwargs)