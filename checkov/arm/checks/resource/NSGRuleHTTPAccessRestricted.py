from checkov.arm.checks.resource.NSGRulePortAccessRestricted import NSGRulePortAccessRestricted


class NSGRuleHTTPAccessRestricted(NSGRulePortAccessRestricted):
    def __init__(self) -> None:
        super().__init__(
            name="Ensure that HTTP (port 80) access is restricted from the internet",
            check_id="CKV_AZURE_160",
            port=80,
        )


check = NSGRuleHTTPAccessRestricted()
