from checkov.terraform.checks.resource.ncp.AccessControlGroupInboundRule import AccessControlGroupInboundRule


class AccessControlGroupGRuleInboundPort3389(AccessControlGroupInboundRule):
    def __init__(self):
        super().__init__(check_id="CUSTOM_NCP_ACG_005", port=3389)


check = AccessControlGroupGRuleInboundPort3389()
