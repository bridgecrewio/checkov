from __future__ import annotations

from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchRequirePushRestrictions(BranchSecurity):
    def __init__(self) -> None:
        name = "Ensure GitHub branch protection requires push restrictions"
        id = "CKV_GITHUB_17"
        super().__init__(name=name, id=id)

    def get_evaluated_keys(self) -> list[str]:
        return ["restrictions"]


check = GithubBranchRequirePushRestrictions()
