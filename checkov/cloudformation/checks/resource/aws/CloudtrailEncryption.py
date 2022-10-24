from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudtrailEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure CloudTrail logs are encrypted at rest using KMS CMKs"
        id = "CKV_AWS_35"
        supported_resources = ("AWS::CloudTrail::Trail",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/KMSKeyId"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = CloudtrailEncryption()
