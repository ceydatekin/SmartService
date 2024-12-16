from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from ..models.models import SmartFeature, SmartModel
from ..domain.rules import ModelBusinessRules
from ..domain.events import FeatureAdded
from ..utils.monitoring import monitor
from ..utils.cache import cached
from .base import BaseService


class FeatureService(BaseService):
    @monitor("add_feature")
    def add_feature(
            self,
            model_id: str,
            data: Dict[str, Any],
            user_id: str
    ) -> SmartFeature:
        """Add a new feature to a model"""
        try:
            # Validate input
            self.validate(data)

            # Get model
            model = self.session.query(SmartModel).get(model_id)
            if not model:
                raise ValueError(f"Model not found: {model_id}")

            # Create feature
            feature = SmartFeature(
                model_id=model_id,
                name=data['name'],
                description=data.get('description'),
                feature_type=data['feature_type'],
                parameters=data.get('parameters', {}),
                response_schema=data.get('response_schema', {}),
                constraints=data.get('constraints', {}),
                created_by=user_id
            )

            # Validate feature addition
            ModelBusinessRules.validate_feature_addition(model, feature)

            self.session.add(feature)
            self.commit()

            # Publish event
            event = FeatureAdded(
                model_id=model_id,
                feature_id=feature.id,
                feature_type=feature.feature_type,
                added_by=user_id,
                metadata=data
            )
            self.event_publisher.publish(event)

            return feature

        except Exception as e:
            self.session.rollback()
            raise e

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate feature data"""
        required_fields = ['name', 'feature_type']
        for field in required_fields:
            if field not in data:
                raise BusinessRuleValidationError(f"Missing required field: {field}")

        if 'parameters' in data and not isinstance(data['parameters'], dict):
            raise BusinessRuleValidationError(
                "Parameters must be a dictionary"
            )

        if 'response_schema' in data and not isinstance(data['response_schema'], dict):
            raise BusinessRuleValidationError(
                "Response schema must be a dictionary"
            )

        return True