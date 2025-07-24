from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import (
    BaseResourceValueCheck,
)


class KMSKeyIsEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure KMS key is enabled"
        id = "CKV_AWS_227"
        supported_resources = ('awscc_kms_key',)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "enabled"


check = KMSKeyIsEnabled()
