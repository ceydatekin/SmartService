import grpc
from concurrent import futures
from sqlalchemy.orm import Session
from ..utils.cache import cached
from ..utils.monitoring import monitor
from ..models.models import SmartModel, SmartFeature


class SmartServiceServicer:
    def __init__(self, session: Session):
        self.session = session

    @monitor("create_model")
    def create_model(self, request, context):
        try:
            model = SmartModel(
                name=request.name,
                type=request.type,
                category=request.category,
                description=request.description
            )

            self.session.add(model)
            self.session.commit()

            return model

        except Exception as e:
            self.session.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None

    @monitor("get_model")
    @cached("model")
    def get_model(self, id: str, context):
        try:
            model = self.session.query(SmartModel).filter(
                SmartModel.id == id
            ).first()

            if not model:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Model not found: {id}")
                return None

            return model

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None

    @monitor("list_models")
    def list_models(self, request, context):
        try:
            query = self.session.query(SmartModel)

            # Apply filters
            if request.type:
                query = query.filter(SmartModel.type == request.type)
            if request.category:
                query = query.filter(SmartModel.category == request.category)

            return query.all()

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return []