from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from src.domain.rules import BusinessRuleValidationError
from src.models.models import SmartModel, ModelType
from src.services.base import BaseService
from src.utils.monitoring import monitor

class ModelService(BaseService):
    def __init__(self, session: Session, cache=None):
        super().__init__(session, cache)

    @monitor("create_model")
    async def create_model(self, data: Dict[str, Any], user_id: str) -> SmartModel:
        """Create a new model"""
        try:
            self.validate(data)

            model = SmartModel(
                name=data['name'],
                type=ModelType(data['type']),
                category=data.get('category'),
                description=data.get('description'),
                version=data.get('version', '1.0'),
                meta_info=data.get('meta_info', {}),
                configuration=data.get('configuration', {}),
                capabilities=data.get('capabilities', []),
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
                raise BusinessRuleValidationError(f"Missing required fields: {field}")  # field -> fields

        # Type validation
        if 'type' in data and not isinstance(data['type'], ModelType):
            try:
                data['type'] = ModelType(data['type'])
            except ValueError:
                raise BusinessRuleValidationError(f"Invalid model type: {data['type']}")

        return True

    @monitor("get_model")
    async def get_model(self, model_id: str) -> Optional[SmartModel]:
        if self.cache:
            cached = self.cache.get(f"model:{model_id}")
            if cached:
                return cached

        model = self.session.query(SmartModel).filter(
            SmartModel.id == model_id
        ).first()

        if model and self.cache:
            self.cache.set(f"model:{model_id}", model)

        return model

    @monitor("list_models")
    async def list_models(self, filters: Dict[str, Any] = None) -> list[SmartModel]:
        query = self.session.query(SmartModel)

        if filters:
            if 'type' in filters:
                query = query.filter(SmartModel.type == filters['type'])
            if 'category' in filters:
                query = query.filter(SmartModel.category == filters['category'])

        return query.all()