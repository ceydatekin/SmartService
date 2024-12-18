from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Generic, TypeVar, Optional
from src.domain.rules import BusinessRuleValidationError
from src.models.models import ModelType, FeatureType

T = TypeVar('T')

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    field: Optional[str] = None

    @property
    def message(self) -> str:
        return "; ".join(self.errors)


class DomainValidator(ABC, Generic[T]):
    def __init__(self):
        self._errors: List[str] = []
        self._field_errors: dict[str, List[str]] = {}

    @abstractmethod
    def validate(self, entity: T) -> ValidationResult:
        pass

    def add_error(self, message: str, field: Optional[str] = None):
        if field:
            if field not in self._field_errors:
                self._field_errors[field] = []
            self._field_errors[field].append(message)
        self._errors.append(message)

    def get_validation_result(self, field: Optional[str] = None) -> ValidationResult:
        errors = self._field_errors.get(field, []) if field else self._errors
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            field=field
        )

    def validate_and_raise(self, entity: T, field: Optional[str] = None):
        result = self.validate(entity)
        if not result.is_valid:
            raise BusinessRuleValidationError(result.message)
        return True


class ModelValidator(DomainValidator['SmartModel']):
    def __init__(self, min_name_length: int = 3):
        super().__init__()
        self.min_name_length = min_name_length

    def validate(self, model: 'SmartModel') -> ValidationResult:
        self._validate_name(model.name)
        self._validate_type(model.type)
        self._validate_category(model.category)
        self._validate_configuration(model.configuration)

        return self.get_validation_result()

    def _validate_name(self, name: str):
        if not name:
            self.add_error("Name is required", "name")
        elif len(name) < self.min_name_length:
            self.add_error(
                f"Name must be at least {self.min_name_length} characters",
                "name"
            )

    def _validate_type(self, type_: ModelType):
        if not type_:
            self.add_error("Type is required", "type")
        elif not isinstance(type_, ModelType):
            self.add_error(f"Invalid model type: {type_}", "type")

    def _validate_category(self, category: str):
        if not category:
            self.add_error("Category is required", "category")

    def _validate_configuration(self, config: dict):
        if config and not isinstance(config, dict):
            self.add_error("Configuration must be a dictionary", "configuration")


class FeatureValidator(DomainValidator['SmartFeature']):
    def __init__(self, min_name_length: int = 3):
        super().__init__()
        self.min_name_length = min_name_length

    def validate(self, feature: 'SmartFeature') -> ValidationResult:
        self._validate_name(feature.name)
        self._validate_type(feature.feature_type)
        self._validate_parameters(feature.parameters)

        return self.get_validation_result()

    def _validate_name(self, name: str):
        if not name:
            self.add_error("Name is required", "name")
        elif len(name) < self.min_name_length:
            self.add_error(
                f"Name must be at least {self.min_name_length} characters",
                "name"
            )

    def _validate_type(self, type_: FeatureType):
        if not type_:
            self.add_error("Feature type is required", "feature_type")
        elif not isinstance(type_, FeatureType):
            self.add_error(f"Invalid feature type: {type_}", "feature_type")

    def _validate_parameters(self, parameters: dict):
        if parameters and not isinstance(parameters, dict):
            self.add_error("Parameters must be a dictionary", "parameters")