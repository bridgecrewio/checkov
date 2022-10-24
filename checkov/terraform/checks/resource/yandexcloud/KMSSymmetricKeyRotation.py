from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class KMSSymmetricKeyRotation(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure KMS symmetric key is rotated."
        id = "CKV_YC_9"
        supported_resources = ("yandex_kms_symmetric_key",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "rotation_period"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = KMSSymmetricKeyRotation()
