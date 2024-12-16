from typing import Dict, Any
from sqlalchemy.orm import Session
from ..models.models import SmartModel
from .base import BaseService
from ..utils.monitoring import monitor


class ModelService(BaseService):
    @monitor("create_model")
    def create_model(self, data: Dict[str, Any], user_id: str) -> SmartModel:
        """Create a new model"""
        try:
            self.validate(data)

            model = SmartModel(
                name=data['name'],
                type=data['type'],
                version=data.get('version', '1.0'),
                meta_info=data.get('meta_info', {}),
                configuration=data.get('configuration', {}),
                capabilities=data.get('capabilities', {}),
                created_by=user_id
            )

            self.session.add(model)
            self.commit()

            return model
        except Exception as e:
            self.handle_error(e, context={'data': data, 'user_id': user_id})

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate model data"""
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return True