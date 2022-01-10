from checkov.github.base_github_org_security import OrgSecurity


class Github2FA(OrgSecurity):
    def __init__(self):
        name = "Ensure GitHub organization security settings require 2FA"
        id = "CKV_GITHUB_1"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self):
        return ['data/organization/requiresTwoFactorAuthentication']


check = Github2FA()
