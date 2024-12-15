import os

from dotenv import load_dotenv
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import enum
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class ModelType(enum.Enum):
    DEVICE = "DEVICE"
    SERVICE = "SERVICE"

class FeatureStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    MAINTENANCE = "MAINTENANCE"

# .env dosyasını yükle
load_dotenv()

# Veritabanı bağlantı bilgileri
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Engine oluşturma
engine = create_engine(DATABASE_URL)

# Session oluşturucu
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model
Base = declarative_base()


class SmartModel(Base):
    __tablename__ = "smart_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    type = Column(Enum(ModelType, name="model_type_enum"), nullable=False)
    category = Column(String(50), nullable=False,index=True)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    features = relationship("SmartFeature", back_populates="model", cascade="all, delete-orphan",passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if self.type else None,
            "category": self.category,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "features": [feature.to_dict() for feature in self.features]
        }

class SmartFeature(Base):
    __tablename__ = "smart_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(36), ForeignKey('smart_models.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    function_type = Column(String(50), nullable=False)
    status = Column(Enum(FeatureStatus, name="feature_status_enum"), default=FeatureStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    model = relationship("SmartModel", back_populates="features",passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "function_type": self.function_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# Database Session yöneticisi
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Tabloları oluştur
def create_tables():
    Base.metadata.create_all(bind=engine)