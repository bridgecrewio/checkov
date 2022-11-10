from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ServerPublicIP(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Server instance should not have public IP."
        id = "CKV_NCP_23"
        supported_resource = ('ncloud_public_ip',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf):
        if 'server_instance_no' in conf.keys():
            return CheckResult.FAILED
        return CheckResult.PASSED


check = ServerPublicIP()
