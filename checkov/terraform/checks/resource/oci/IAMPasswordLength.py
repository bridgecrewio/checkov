from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class IAMPasswordLength(BaseResourceCheck):
    def __init__(self):
        name = "OCI IAM password policy for local (non-federated) users has a minimum 14 characters"
        id = "CKV_OCI_18"
        supported_resources = ['oci_identity_authentication_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'password_policy' in conf.keys():
            rules = conf.get("password_policy")[0]
            if 'minimum_password_length' in rules:
                passwordlength=rules.get("minimum_password_length")
                if passwordlength[0] < 14:
                    return CheckResult.FAILED
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED

check = IAMPasswordLength()
