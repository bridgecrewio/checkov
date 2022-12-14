from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.github.base_github_org_check import BaseOrganizationCheck


class GithubRequireOrganizationIsVerified(BaseOrganizationCheck):
    def __init__(self) -> None:
        name = "Ensure an organization's identity is confirmed with a Verified badge Passed"
        id = "CKV_GITHUB_28"
        super().__init__(id=id, name=name, missing_attribute_result=CheckResult.FAILED)

    def get_evaluated_keys(self) -> list[str]:
        return ["is_verified"]

    def get_allowed_values(self) -> list[Any]:
        return [True]


check = GithubRequireOrganizationIsVerified()
