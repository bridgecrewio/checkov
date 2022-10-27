from checkov.terraform.checks.resource.ncp.AccessControlGroupInboundRule import AccessControlGroupInboundRule


class AccessControlGroupRuleInboundPort3389(AccessControlGroupInboundRule):
    def __init__(self):
        super().__init__(check_id="CKV_NCP_5", port=3389)


check = AccessControlGroupRuleInboundPort3389()
