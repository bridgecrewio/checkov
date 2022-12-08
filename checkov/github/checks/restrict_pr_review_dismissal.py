from __future__ import annotations

from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.github.base_github_negative_branch_security import NegativeBranchSecurity


class GithubBranchDismissalRestrictions(NegativeBranchSecurity):
    def __init__(self) -> None:
        name = "Ensure GitHub branch protection restricts who can dismiss PR reviews"
        id = "CKV_GITHUB_12"
        super().__init__(name=name, id=id)

    def get_evaluated_keys(self) -> list[str]:
        return ["required_pull_request_reviews/dismissal_restrictions"]

    def get_forbidden_values(self) -> list[Any]:
        return [ANY_VALUE]


check = GithubBranchDismissalRestrictions()
