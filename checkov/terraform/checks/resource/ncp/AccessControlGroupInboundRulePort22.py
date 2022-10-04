from checkov.terraform.checks.resource.ncp.AccessControlGroupInboundRule import AccessControlGroupInboundRule


class AccessControlGroupGRuleInboundPort22(AccessControlGroupInboundRule):
    def __init__(self):
        super().__init__(check_id="CUSTOM_NCP_ACG_003", port=22)


check = AccessControlGroupGRuleInboundPort22()
