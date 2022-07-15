from checkov.terraform.checks.resource.alicloud.AbsRDSParameter import AbsRDSParameter


class RDSInstanceLogsEnabled(AbsRDSParameter):
    def __init__(self):
        super().__init__(check_id="CKV_ALI_35", parameter="log_duration")


check = RDSInstanceLogsEnabled()
