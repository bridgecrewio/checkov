from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class EBSDefaultEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure EBS default encryption is enabled"
        id = "CKV_AWS_106"
        supported_resources = ["aws_ebs_encryption_by_default"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        enabled = conf.get("enabled")
        if enabled and enabled == [False]:
            return CheckResult.FAILED
        else:
            return CheckResult.PASSED


check = EBSDefaultEncryption()
