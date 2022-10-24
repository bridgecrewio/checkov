from __future__ import annotations

from checkov.github.base_github_org_security import OrgSecurity


class GithubIPAllowList(OrgSecurity):
    def __init__(self) -> None:
        name = "Ensure GitHub organization security settings has IP allow list enabled"
        id = "CKV_GITHUB_3"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self) -> list[str]:
        return ['data/organization/ipAllowListForInstalledAppsEnabledSetting']

    def get_expected_value(self) -> str:
        return "ENABLED"


check = GithubIPAllowList()
