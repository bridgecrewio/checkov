from checkov.github.base_github_org_security import OrgSecurity


class Github2FA(OrgSecurity):
    def __init__(self):
        name = "Ensure GitHub organization security settings has IP allow list enabled"
        id = "CKV_GITHUB_3"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self):
        return ['data/organization/ipAllowListForInstalledAppsEnabledSetting']

    def get_expected_value(self):
        return "ENABLED"


check = Github2FA()
