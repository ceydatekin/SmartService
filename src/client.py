import grpc
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src import smart_service_pb2 as pb2
from src import smart_service_pb2_grpc as pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.SmartServiceStub(channel)

    try:
        print("\n1. Smart Model Oluşturuluyor...")
        model_request = pb2.CreateModelRequest(
            model=pb2.SmartModel(
                name="Akıllı Kamera",
                type="DEVICE",
                category="camera",
                description="360 derece dönebilen güvenlik kamerası"
            )
        )
        response = stub.CreateModel(model_request)
        print(f"Model oluşturuldu: ID = {response.id}")
        model_id = response.id

        print("\n2. Model Bilgileri Alınıyor...")
        get_response = stub.GetModel(pb2.GetModelRequest(id=model_id))
        print(f"Model bulundu: {get_response.model.name}")

        print("\n3. Smart Feature Oluşturuluyor...")
        feature_request = pb2.CreateFeatureRequest(
            feature=pb2.SmartFeature(
                model_id=model_id,
                name="Fotoğraf Çek",
                description="Anlık fotoğraf çekme özelliği",
                function_type="capture"
            )
        )
        feature_response = stub.CreateFeature(feature_request)
        print(f"Feature oluşturuldu: ID = {feature_response.id}")

        print("\n4. Tüm Modeller Listeleniyor...")
        list_response = stub.ListModels(pb2.ListModelsRequest())
        for model in list_response.models:
            print(f"- {model.name} ({model.type}): {model.description}")

    except grpc.RpcError as e:
        print(f"Hata oluştu: {e.details()}")


if __name__ == '__main__':
    run()