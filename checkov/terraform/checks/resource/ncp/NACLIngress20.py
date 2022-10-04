from checkov.terraform.checks.resource.ncp.NACLIngressCheck import NACLIngressCheck


class NACLIngress20(NACLIngressCheck):
    def __init__(self):
        super().__init__(check_id="CKV_NCP_230", port=20)


check = NACLIngress20()