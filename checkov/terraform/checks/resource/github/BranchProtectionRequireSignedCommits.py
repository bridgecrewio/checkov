from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class BranchProtectionRequireSignedCommits(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure all commits GPG signed"
        id = "CKV_GIT_6"
        supported_resources = ["github_branch_protection_v3", "github_branch_protection"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "require_signed_commits"

    def get_expected_value(self) -> Any:
        return True


check = BranchProtectionRequireSignedCommits()
