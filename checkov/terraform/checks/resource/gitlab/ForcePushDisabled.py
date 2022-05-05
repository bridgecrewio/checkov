from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ForcePushDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure force push is disabled"
        id = "CKV_GLB_2"
        supported_resources = ["gitlab_branch_protection"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "allow_force_push"

    def get_expected_value(self) -> Any:
        return False


check = ForcePushDisabled()
