import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

class DomainEvent:
    def __init__(self):
        self.timestamp = datetime.utcnow()
        self.event_id = str(uuid.uuid4())

@dataclass
class ModelCreated(DomainEvent):
    model_id: str
    created_by: str
    model_type: str
    metadata: Dict[str, Any]

@dataclass
class ModelStatusChanged(DomainEvent):
    model_id: str
    old_status: str
    new_status: str
    changed_by: str
    reason: Optional[str] = None

@dataclass
class FeatureAdded(DomainEvent):
    model_id: str
    feature_id: str
    feature_type: str
    added_by: str
    metadata: Dict[str, Any]

@dataclass
class IntegrationConfigured(DomainEvent):
    model_id: str
    integration_id: str
    integration_type: str
    configured_by: str
    config: Dict[str, Any]