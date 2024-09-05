from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories

class SagemakerEndpointConfigurationEndpointNameSpecified(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon SageMaker endpoint has a name specified"
        id = "CKV_AWS_990"
        supported_resources = ['aws_sagemaker_endpoint_configuration']
        categories = [CheckCategories.AI_AND_ML]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "name"

    def get_expected_value(self):
        return ANY_VALUE

check = SagemakerEndpointConfigurationEndpointNameSpecified()
