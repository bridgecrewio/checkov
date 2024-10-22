from checkov.terraform.checks.resource.ncp.NACLInboundCheck import NACLInboundCheck


class NACLInbound20(NACLInboundCheck):
    def __init__(self) -> None:
        super().__init__(check_id="CKV_NCP_8", port=20)


check = NACLInbound20()
