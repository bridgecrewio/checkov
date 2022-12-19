from __future__ import annotations

from checkov.azure_devops.checks.base_policy_check import BasePolicyCheck


class CreatorApproval(BasePolicyCheck):
    def __init__(self) -> None:
        name = "Ensure pull request creators are not allowed to approve their own changes"
        id = "CKV_AZUREDEVOPS_2"
        super().__init__(
            name=name,
            id=id,
            policy_type_id="fa4e907d-c16b-4a4c-9dfa-4906e5d171dd",  # Minimum number of reviewers
        )

    def get_evaluated_keys(self) -> list[str]:
        return ["settings/creatorVoteCounts"]

    def get_expected_value(self) -> bool:
        return False


check = CreatorApproval()
