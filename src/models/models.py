from sqlalchemy import Column, String, JSON, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum as PyEnum

Base = declarative_base()


class ModelType(PyEnum):
    DEVICE = "DEVICE"
    SERVICE = "SERVICE"


class ModelStatus(PyEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    MAINTENANCE = "MAINTENANCE"


class SmartModel(Base):
    __tablename__ = "smart_models"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(Enum(ModelType), nullable=False)
    status = Column(Enum(ModelStatus), default=ModelStatus.DRAFT)
    version = Column(String(50), nullable=False)

    # Model özellikleri - metadata yerine meta_info kullanıyoruz
    meta_info = Column(JSON)  # Genişletilebilir özellikler
    configuration = Column(JSON)  # Model konfigürasyonu
    capabilities = Column(JSON)  # Yetenekler

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    is_active = Column(Boolean, default=True)

    # Relationships
    features = relationship("SmartFeature", back_populates="model", cascade="all, delete-orphan")
    integrations = relationship("ModelIntegration", back_populates="model", cascade="all, delete-orphan")


class SmartFeature(Base):
    __tablename__ = "smart_features"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(36), ForeignKey('smart_models.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    feature_type = Column(String(50), nullable=False)

    # Feature detayları
    parameters = Column(JSON)  # Giriş parametreleri
    response_schema = Column(JSON)  # Çıkış şeması
    constraints = Column(JSON)  # Kısıtlar

    # Teknik detaylar
    endpoint = Column(String(255))
    method = Column(String(50))
    rate_limit = Column(JSON)

    # Status ve güvenlik
    is_active = Column(Boolean, default=True)
    requires_auth = Column(Boolean, default=False)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String(255))

    # Relationships
    model = relationship("SmartModel", back_populates="features")


class ModelIntegration(Base):
    __tablename__ = "model_integrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(36), ForeignKey('smart_models.id'), nullable=False)
    name = Column(String(255), nullable=False)
    integration_type = Column(String(50), nullable=False)
    config = Column(JSON)
    status = Column(String(50), default='ACTIVE')

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationship
    model = relationship("SmartModel", back_populates="integrations")