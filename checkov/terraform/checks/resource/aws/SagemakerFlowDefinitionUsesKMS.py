from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class SagemakerFlowDefinitionUsesKMS(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon SageMaker Flow Definition uses KMS for output configurations"
        id = "CKV_AWS_372"
        supported_resources = ['aws_sagemaker_flow_definition']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "output_config/[0]/kms_key_id"

    def get_expected_value(self):
        return ANY_VALUE


check = SagemakerFlowDefinitionUsesKMS()
