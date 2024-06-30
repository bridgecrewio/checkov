from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SagemakerNotebookInstanceAllowsIMDSv2(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon SageMaker Notebook Instance only allows for IMDSv2"
        id = "CKV_AWS_371"
        supported_resources = ['aws_sagemaker_notebook_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'instance_metadata_service_configuration/[0]/minimum_instance_metadata_service_version'

    def get_expected_value(self):
        return "2"


check = SagemakerNotebookInstanceAllowsIMDSv2()
