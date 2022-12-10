from __future__ import annotations

from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchDismissStaleReviews(BranchSecurity):
    def __init__(self) -> None:
        name = "Ensure GitHub branch protection dismisses stale review on new commit"
        id = "CKV_GITHUB_11"
        super().__init__(name=name, id=id)

    def get_evaluated_keys(self) -> list[str]:
        return ["required_pull_request_reviews/dismiss_stale_reviews"]


check = GithubBranchDismissStaleReviews()
