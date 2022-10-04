from checkov.terraform.checks.resource.ncp.NACLIngressCheck import NACLIngressCheck


class NACLIngress22(NACLIngressCheck):
    def __init__(self):
        super().__init__(check_id="CKV_NCP_232", port=22)


check = NACLIngress22()