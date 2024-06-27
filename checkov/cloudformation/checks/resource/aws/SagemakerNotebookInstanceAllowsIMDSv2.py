from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class SagemakerNotebookInstanceAllowsIMDSv2(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon SageMaker Notebook Instance only allows for IMDSv2"
        id = "CKV_AWS_371"
        supported_resources = ["AWS::SageMaker::NotebookInstance"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/InstanceMetadataServiceConfiguration/MinimumInstanceMetadataServiceVersion'

    def get_expected_value(self):
        return "2"


check = SagemakerNotebookInstanceAllowsIMDSv2()
