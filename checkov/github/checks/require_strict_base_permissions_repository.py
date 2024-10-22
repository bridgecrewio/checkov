from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.github.base_github_org_check import BaseOrganizationCheck


class GithubRequireStrictBasePermissionsRepository(BaseOrganizationCheck):
    def __init__(self) -> None:
        # https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/setting-base-permissions-for-an-organization
        name = "Ensure strict base permissions are set for repositories"
        id = "CKV_GITHUB_27"
        super().__init__(id=id, name=name, missing_attribute_result=CheckResult.FAILED)

    def get_evaluated_keys(self) -> list[str]:
        return ["default_repository_permission"]

    def get_allowed_values(self) -> list[Any]:
        return ['read', None]


check = GithubRequireStrictBasePermissionsRepository()
