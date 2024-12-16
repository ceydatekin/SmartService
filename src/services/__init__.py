from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from ..domain.rules import BusinessRuleValidationError
from ..utils.monitoring import monitor
from ..utils.cache import cached

class BaseService(ABC):
    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        pass