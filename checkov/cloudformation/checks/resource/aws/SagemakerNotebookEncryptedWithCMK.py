from typing import List

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class SagemakerNotebookEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Sagemaker domain and notebook instance are encrypted by KMS using a customer managed Key (CMK)"
        id = "CKV_AWS_187"
        supported_resources = ("AWS::SageMaker::NotebookInstance", "AWS::SageMaker::Domain")
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/KmsKeyId'

    def get_expected_value(self):
        return ANY_VALUE

    def get_evaluated_keys(self) -> List[str]:
        return ['Properties/KmsKeyId']


check = SagemakerNotebookEncryptedWithCMK()
