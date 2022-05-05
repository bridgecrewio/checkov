from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RejectUnsignedCommits(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure commits are signed"
        id = "CKV_GLB_4"
        supported_resources = ["gitlab_project"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "push_rules/[0]/reject_unsigned_commits"

    def get_expected_value(self) -> Any:
        return True


check = RejectUnsignedCommits()
