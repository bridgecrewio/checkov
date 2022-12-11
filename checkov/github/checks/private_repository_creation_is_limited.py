from __future__ import annotations

from checkov.github.repository_creation_is_limited import RepositoryCreationIsLimited


class GithubPrivateRepositoryCreationIsLimited(RepositoryCreationIsLimited):
    def __init__(self) -> None:
        name = "Ensure private repository creation is limited to specific members"
        id = "CKV_GITHUB_22"
        super().__init__(id=id, name=name)

    def get_evaluated_keys(self) -> list[str]:
        return ["members_can_create_private_repositories"]


check = GithubPrivateRepositoryCreationIsLimited()
