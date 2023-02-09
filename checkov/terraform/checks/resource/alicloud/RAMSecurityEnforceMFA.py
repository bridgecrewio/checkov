from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RAMSecurityEnforceMFA(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure RAM enforces MFA"
        id = "CKV_ALI_24"
        supported_resources = ("alicloud_ram_security_preference",)
        categories = (CheckCategories.IAM,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.FAILED,
        )

    def get_inspected_key(self) -> str:
        return "enforce_mfa_for_login"


check = RAMSecurityEnforceMFA()
