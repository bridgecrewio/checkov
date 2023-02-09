from __future__ import annotations

from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchAdminEnforcement(BranchSecurity):
    def __init__(self) -> None:
        name = "Ensure branch protection rules are enforced on administrators"
        id = "CKV_GITHUB_10"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self) -> list[str]:
        return ['enforce_admins/enabled']


check = GithubBranchAdminEnforcement()
