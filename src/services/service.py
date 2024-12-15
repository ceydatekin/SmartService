import grpc
from concurrent import futures
from sqlalchemy.orm import Session

# Fix imports
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import smart_service_pb2 as pb2
from src import smart_service_pb2_grpc as pb2_grpc
from src.models.models import SmartModel, SmartFeature, ModelType


class SmartServiceServicer(pb2_grpc.SmartServiceServicer):
    def __init__(self, session_maker):
        self.SessionMaker = session_maker

    def CreateModel(self, request, context):
        with self.SessionMaker() as session:
            try:
                model = SmartModel(
                    name=request.model.name,
                    type=ModelType[request.model.type],  # Enum conversion
                    category=request.model.category,
                    description=request.model.description
                )
                session.add(model)
                session.commit()
                session.refresh(model)

                return pb2.SmartModel(
                    id=model.id,
                    name=model.name,
                    type=model.type.name,  # Convert enum to string
                    category=model.category,
                    description=model.description
                )
            except Exception as e:
                session.rollback()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.SmartModel()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_SmartServiceServicer_to_server(
        SmartServiceServicer(None), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()