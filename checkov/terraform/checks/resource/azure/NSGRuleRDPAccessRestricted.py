from checkov.terraform.checks.resource.azure.NSGRulePortAccessRestricted import NSGRulePortAccessRestricted


class NSGRuleRDPAccessRestricted(NSGRulePortAccessRestricted):
    def __init__(self):
        super().__init__(name="Ensure that RDP access is restricted from the internet", check_id="CKV_AZURE_9", port=3389)


check = NSGRuleRDPAccessRestricted()
