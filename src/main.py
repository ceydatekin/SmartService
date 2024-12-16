import os
import sys
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base  # Relative import kullanalım
from services.service import serve
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    try:
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'password123')
        DB_HOST = os.getenv('DB_HOST', 'postgres')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'smartdb')

        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        logger.info(f"Connecting to database at {DB_HOST}:{DB_PORT}/{DB_NAME}")

        engine = create_engine(DATABASE_URL)

        # Create tables
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")

        return engine
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


if __name__ == '__main__':
    try:
        engine = init_db()
        SessionLocal = sessionmaker(bind=engine)
        logger.info("Starting gRPC server...")
        serve(SessionLocal)
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)