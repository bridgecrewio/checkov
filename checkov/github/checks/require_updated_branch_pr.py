from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.github.base_github_negative_branch_security import NegativeBranchSecurity


class GithubRequireUpdatedBranch(NegativeBranchSecurity):
    def __init__(self) -> None:
        name = "Ensure open git branches are up to date before they can be merged into codebase"
        id = "CKV_GITHUB_20"
        super().__init__(name=name, id=id, missing_attribute_result=CheckResult.FAILED)

    def get_evaluated_keys(self) -> list[str]:
        return ["required_status_checks/strict"]

    def get_forbidden_values(self) -> list[Any]:
        return [False]


check = GithubRequireUpdatedBranch()
