from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class KMSKeyRotationIsEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure KMS Key Rotation is enabled"
        id = "CKV_ALI_27"
        supported_resources = ['alicloud_kms_key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "automatic_rotation"

    def get_expected_value(self) -> Any:
        return "Enabled"


check = KMSKeyRotationIsEnabled()
