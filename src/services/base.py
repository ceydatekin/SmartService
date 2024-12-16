from abc import ABC, abstractmethod
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..utils.cache import Cache
from ..domain.rules import BusinessRuleValidationError
import logging

logger = logging.getLogger(__name__)

class BaseService(ABC):
    def __init__(self, session: Session, cache: Cache = None):
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

    def clear_cache(self, key_pattern: str):
        """Cache temizleme"""
        if self.cache:
            try:
                self.cache.delete_pattern(key_pattern)
            except Exception as e:
                logger.error(f"Cache clear failed: {str(e)}")

    def begin_transaction(self):
        """Transaction başlatma"""
        return self.session.begin_nested()

    def handle_error(self, error: Exception, context: Dict[str, Any] = None):
        """Hata yönetimi"""
        self.session.rollback()
        logger.error(f"Service error: {str(error)}, Context: {context}")
        raise error