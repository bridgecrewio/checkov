from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class MongoDBIsPublic(BaseResourceCheck):
    def __init__(self):
        name = "Ensure MongoDB instance is not public"
        id = "CKV_ALI_43"
        supported_resources = ['alicloud_mongodb_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        security_ip_list = conf.get("security_ip_list")
        if security_ip_list and isinstance(security_ip_list, list):
            addresses = security_ip_list[0]
            if "0.0.0.0" in addresses or "0.0.0.0/0" in addresses:  # nosec B104
                self.evaluated_keys = ['security_ip_list']
                return CheckResult.FAILED
        return CheckResult.PASSED


check = MongoDBIsPublic()
