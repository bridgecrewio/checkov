from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SageMakerInternetAccessDisabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that direct internet access is disabled for an Amazon SageMaker Notebook Instance"
        id = "CKV_AWS_122"
        supported_resources = ['aws_sagemaker_notebook_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'direct_internet_access'

    def get_expected_value(self):
        return 'Disabled'


check = SageMakerInternetAccessDisabled()
