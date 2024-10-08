from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories

class SagemakerNotebookLifecycleConfigSpecified(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon SageMaker notebook instances use lifecycle configurations"
        id = "CKV_AWS_377"
        supported_resources = ['aws_sagemaker_notebook_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "lifecycle_config_name"

    def get_expected_value(self):
        return ANY_VALUE

check = SagemakerNotebookLifecycleConfigSpecified()
