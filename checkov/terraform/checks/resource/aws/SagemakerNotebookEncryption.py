from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SagemakerNotebookEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure SageMaker Notebook is encrypted at rest using KMS CMK"
        id = "CKV_AWS_22"
        supported_resources = ['aws_sagemaker_notebook_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'kms_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = SagemakerNotebookEncryption()
