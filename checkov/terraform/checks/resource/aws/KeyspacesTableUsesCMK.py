from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class KeyspacesTableUsesCMK(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Keyspaces Table uses CMK"
        id = "CKV_AWS_265"
        supported_resources = ['aws_keyspaces_table']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("encryption_specification") and isinstance(conf.get("encryption_specification"), list):
            encrypt = conf.get("encryption_specification")[0]
            if encrypt.get("kms_key_identifier") and isinstance(encrypt.get("kms_key_identifier"), list):
                if encrypt.get("type") == ["CUSTOMER_MANAGED_KEY"]:
                    return CheckResult.PASSED
                self.evaluated_keys = ["encryption_specification/[0]/type"]
            self.evaluated_keys = ["encryption_specification/[0]/kms_key_identifier"]
        self.evaluated_keys = ["encryption_specification"]
        return CheckResult.FAILED


check = KeyspacesTableUsesCMK()
