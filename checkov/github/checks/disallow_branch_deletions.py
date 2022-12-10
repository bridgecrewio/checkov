from __future__ import annotations

from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchDisallowDeletions(BranchSecurity):
    def __init__(self) -> None:
        name = "Ensure GitHub branch protection rules does not allow deletions"
        id = "CKV_GITHUB_18"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self) -> list[str]:
        return ['allow_deletions/enabled']

    def get_expected_value(self) -> bool:
        return False


check = GithubBranchDisallowDeletions()
