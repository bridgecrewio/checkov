from __future__ import annotations

from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchRequireCodeOwnerReviews(BranchSecurity):
    def __init__(self) -> None:
        name = "Ensure GitHub branch protection requires CODEOWNER reviews"
        id = "CKV_GITHUB_13"
        super().__init__(name=name, id=id)

    def get_evaluated_keys(self) -> list[str]:
        return ["required_pull_request_reviews/require_code_owner_reviews"]


check = GithubBranchRequireCodeOwnerReviews()
