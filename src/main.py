import sys
import os

# Path ayarı - modülleri bulabilmek için
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.models.models import create_tables
from src.services.service import serve
from dotenv import load_dotenv


def init():
    # .env dosyasını yükle
    load_dotenv()

    # Veritabanı tablolarını oluştur
    create_tables()
    print("Database tables created successfully")


if __name__ == '__main__':
    try:
        init()
        print("Starting gRPC server...")
        serve()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)