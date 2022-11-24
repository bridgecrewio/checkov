from __future__ import annotations

from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchDismissalRestrictions(BranchSecurity):
    def __init__(self) -> None:
        name = " Ensure GitHub branch protection restricts who can dismiss PR reviews - CIS 1.1.5"
        id = "CKV_GITHUB_12"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self) -> list[str]:
        return (['required_pull_request_reviews/dismissal_restrictions'])

    def get_expected_value(self) -> str:
        return None


check = GithubBranchDismissalRestrictions()
