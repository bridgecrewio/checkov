from checkov.terraform.checks.resource.ncp.NACLInboundCheck import NACLInboundCheck


class NACLInbound22(NACLInboundCheck):
    def __init__(self) -> None:
        super().__init__(check_id="CKV_NCP_10", port=22)


check = NACLInbound22()
