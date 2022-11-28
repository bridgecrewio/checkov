from __future__ import annotations

from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchLinearHistory(BranchSecurity):
    def __init__(self) -> None:
        name = "Ensure GitHub branch protection rules requires linear history"
        id = "CKV_GITHUB_8"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self) -> list[str]:
        return ['required_linear_history/enabled']


check = GithubBranchLinearHistory()
