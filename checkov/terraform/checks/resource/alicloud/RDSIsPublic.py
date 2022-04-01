from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RDSIsPublic(BaseResourceCheck):
    def __init__(self):
        name = "Ensure database instance is not public"
        id = "CKV_ALI_9"
        supported_resources = ['alicloud_db_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        security_ips = conf.get("security_ips")
        if security_ips and isinstance(security_ips, list):
            addresses = security_ips[0]
            if "0.0.0.0" in addresses or "0.0.0.0/0" in addresses:  # nosec B104
                self.evaluated_keys = ['security_ips']
                return CheckResult.FAILED
        return CheckResult.PASSED


check = RDSIsPublic()
