from checkov.terraform.checks.resource.ncp.NACLIngressCheck import NACLIngressCheck


class NACLIngress21(NACLIngressCheck):
    def __init__(self):
        super().__init__(check_id="CKV_NCP_229", port=21)


check = NACLIngress21()