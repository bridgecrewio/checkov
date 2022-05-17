from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_int


class RequireTwoApprovalsToMerge(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure at least two approving reviews to merge"
        id = "CKV_GLB_1"
        supported_resources = ["gitlab_project"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        approvals = conf.get("approvals_before_merge")
        if approvals and isinstance(approvals, list):
            num_approvals = force_int(approvals[0])
            if num_approvals and num_approvals >= 2:
                return CheckResult.PASSED
        self.evaluated_keys = ["approvals_before_merge"]
        return CheckResult.FAILED


check = RequireTwoApprovalsToMerge()
