from checkov.terraform.checks.resource.azure.NSGRulePortAccessRestricted import NSGRulePortAccessRestricted


class NSGRuleSSHAccessRestricted(NSGRulePortAccessRestricted):
    def __init__(self) -> None:
        super().__init__(
            name="Ensure that * port access is restricted from the internet",
            check_id="CKV_AZURE_246",
            port="*",
        )


check = NSGRuleSSHAccessRestricted()
