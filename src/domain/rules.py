from ..models.models import SmartModel, SmartFeature, ModelStatus


class BusinessRuleValidationError(Exception):
    pass


class ModelBusinessRules:
    @staticmethod
    def validate_model_activation(model: SmartModel) -> bool:
        if not model.features:
            raise BusinessRuleValidationError(
                "Model must have at least one feature to be activated"
            )

        if not model.configuration:
            raise BusinessRuleValidationError(
                "Model must have configuration before activation"
            )

        if model.status == ModelStatus.DEPRECATED:
            raise BusinessRuleValidationError(
                "Deprecated model cannot be activated"
            )

        return True

    @staticmethod
    def validate_feature_addition(model: SmartModel, feature: SmartFeature) -> bool:
        if len(model.features) >= 10:
            raise BusinessRuleValidationError(
                "Maximum feature limit reached (10)"
            )

        if any(f.name == feature.name for f in model.features):
            raise BusinessRuleValidationError(
                f"Feature name '{feature.name}' already exists"
            )

        if feature.parameters and not model.capabilities:
            raise BusinessRuleValidationError(
                "Model must have capabilities defined for parameterized features"
            )

        return True

    @staticmethod
    def validate_model_deprecation(model: SmartModel) -> bool:
        if model.status == ModelStatus.DRAFT:
            raise BusinessRuleValidationError(
                "Draft model cannot be deprecated"
            )

        if any(i.status == 'ACTIVE' for i in model.integrations):
            raise BusinessRuleValidationError(
                "Model has active integrations and cannot be deprecated"
            )

        return True