from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ECRRepositoryEncrypted(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that ECR repositories are encrypted"
        id = "CKV_AWS_136"
        supported_resources = ("AWS::ECR::Repository",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/EncryptionConfiguration/EncryptionType"

    def get_expected_value(self) -> Any:
        # Valid Values: AES256 | KMS
        return ANY_VALUE


check = ECRRepositoryEncrypted()
