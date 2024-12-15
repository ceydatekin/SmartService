from typing import Optional
from src.models.models import ModelType, FeatureStatus


def validate_model(model) -> bool:
    """Smart Model validasyonu"""
    if not model.name or len(model.name) < 3:
        return False

    if not model.type or model.type not in [t.value for t in ModelType]:
        return False

    if not model.category:
        return False

    return True


def validate_feature(feature) -> bool:
    """Smart Feature validasyonu"""
    if not feature.name or len(feature.name) < 3:
        return False

    if not feature.function_type:
        return False

    if hasattr(feature, 'status') and \
            feature.status not in [s.value for s in FeatureStatus]:
        return False

    return True


def validate_pagination(page: int, size: int) -> tuple[int, int]:
    """Sayfalama parametrelerini doğrula ve varsayılan değerleri ayarla"""
    if page < 0:
        page = 0
    if size < 1 or size > 100:
        size = 10
    return page, size