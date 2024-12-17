from abc import ABC, abstractmethod
from typing import Dict, Any
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class BaseService(ABC):
    def __init__(self, session: Session, cache=None):
        self.session = session
        self.cache = cache

    def commit(self):
        """Güvenli transaction commit"""
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Her servis kendi validation kurallarını implement etmeli"""
        pass

    def handle_error(self, error: Exception, context: Dict[str, Any] = None):
        """Hata yönetimi"""
        self.session.rollback()
        logger.error(f"Service error: {str(error)}, Context: {context}")
        raise error