from __future__ import annotations

from typing import Any

from checkov.azure_devops.checks.base_negative_policy_check import BaseNegativePolicyCheck
from checkov.common.models.enums import CheckResult


class MergeRequestsApprovals(BaseNegativePolicyCheck):
    def __init__(self) -> None:
        name = "Ensure any change to code receives approval of two strongly authenticated users"
        id = "CKV_AZUREDEVOPS_1"
        super().__init__(
            name=name,
            id=id,
            policy_type_id="fa4e907d-c16b-4a4c-9dfa-4906e5d171dd",  # Minimum number of reviewers
            missing_attribute_result=CheckResult.FAILED,
        )

    def get_evaluated_keys(self) -> list[str]:
        return ["settings/minimumApproverCount"]

    def get_forbidden_values(self) -> list[Any]:
        return [None, 0, 1]


check = MergeRequestsApprovals()
