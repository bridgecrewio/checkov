from checkov.terraform.checks.resource.alicloud.AbsRDSParameter import AbsRDSParameter


class RDSInstanceLogConnections(AbsRDSParameter):
    def __init__(self):
        super().__init__(check_id="CKV_ALI_37", parameter="log_connections")


check = RDSInstanceLogConnections()
