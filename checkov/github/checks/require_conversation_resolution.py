from __future__ import annotations

from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchRequireConversationResolution(BranchSecurity):
    def __init__(self) -> None:
        name = "Ensure GitHub branch protection requires conversation resolution"
        id = "CKV_GITHUB_16"
        super().__init__(name=name, id=id)

    def get_evaluated_keys(self) -> list[str]:
        return ["required_conversation_resolution/enabled"]


check = GithubBranchRequireConversationResolution()
