from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from src.models.models import SmartFeature, FeatureType
from src.services.base import BaseService
from src.utils.monitoring import monitor


class FeatureService(BaseService):
    def __init__(self, session: Session, cache=None):
        super().__init__(session, cache)

    @monitor("add_feature")
    async def add_feature(
            self,
            model_id: str,
            data: Dict[str, Any],
            user_id: str
    ) -> SmartFeature:
        try:
            self.validate(data)

            feature = SmartFeature(
                model_id=model_id,
                name=data['name'],
                feature_type=FeatureType(data['feature_type']),
                description=data.get('description'),
                parameters=data.get('parameters', {}),
                response_schema=data.get('response_schema', {}),
                constraints=data.get('constraints', {}),
                created_by=user_id
            )

            self.session.add(feature)
            self.commit()

            return feature

        except Exception as e:
            self.handle_error(e, context={
                'model_id': model_id,
                'data': data,
                'user_id': user_id
            })

    def validate(self, data: Dict[str, Any]) -> bool:
        required_fields = ['name', 'feature_type']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return True