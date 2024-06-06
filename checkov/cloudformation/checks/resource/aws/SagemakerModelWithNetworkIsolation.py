from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class SagemakerModelWithNetworkIsolation(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon SageMaker model uses network isolation"
        id = "CKV_AWS_370"
        supported_resources = ["AWS::SageMaker::Model"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/EnableNetworkIsolation'


check = SagemakerModelWithNetworkIsolation()
