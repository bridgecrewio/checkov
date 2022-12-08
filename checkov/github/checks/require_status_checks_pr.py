from __future__ import annotations

from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchRequireStatusChecks(BranchSecurity):
    def __init__(self) -> None:
        name = "Ensure all checks have passed before the merge of new code"
        id = "CKV_GITHUB_14"
        super().__init__(name=name, id=id)

    def get_evaluated_keys(self) -> list[str]:
        return ["required_status_checks"]


check = GithubBranchRequireStatusChecks()
