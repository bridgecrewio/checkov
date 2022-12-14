from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.github.base_github_org_check import BaseOrganizationCheck


class GithubPrivateRepositoryCreationIsLimited(BaseOrganizationCheck):
    def __init__(self) -> None:
        name = "Ensure private repository creation is limited to specific members"
        id = "CKV_GITHUB_22"
        super().__init__(id=id, name=name, missing_attribute_result=CheckResult.FAILED)

    def get_evaluated_keys(self) -> list[str]:
        return ["members_can_create_private_repositories"]

    def get_allowed_values(self) -> list[Any]:
        return [False]


check = GithubPrivateRepositoryCreationIsLimited()
