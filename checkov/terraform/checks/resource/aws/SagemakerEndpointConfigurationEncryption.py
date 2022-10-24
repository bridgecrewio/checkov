from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class SagemakerEndpointConfigurationEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the Sagemaker Endpoint is securely encrypted at rest"
        id = "CKV_AWS_98"
        supported_resources = ['aws_sagemaker_endpoint_configuration']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'kms_key_arn'

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = SagemakerEndpointConfigurationEncryption()
