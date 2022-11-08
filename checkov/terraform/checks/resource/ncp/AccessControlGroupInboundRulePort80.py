from checkov.terraform.checks.resource.ncp.AccessControlGroupInboundRule import AccessControlGroupInboundRule


class AccessControlGroupRuleInboundPort80(AccessControlGroupInboundRule):
    def __init__(self):
        super().__init__(check_id="CKV_NCP_36", port=80)


check = AccessControlGroupRuleInboundPort80()
