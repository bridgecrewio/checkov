from checkov.arm.checks.resource.NSGRulePortAccessRestricted import NSGRulePortAccessRestricted


class NSGRuleSSHAccessRestricted(NSGRulePortAccessRestricted):
    def __init__(self) -> None:
        super().__init__(
            name="Ensure that SSH access is restricted from the internet", check_id="CKV_AZURE_10", port=22
        )


check = NSGRuleSSHAccessRestricted()
