from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EMRClusterIsEncryptedKMS(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Cluster security configuration encryption is using SSE-KMS"
        id = "CKV_AWS_171"
        supported_resources = ['aws_emr_security_configuration']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'configuration' not in conf:
            return CheckResult.SKIPPED
        self.evaluated_keys = ['configuration']
        configuration = conf['configuration'][0]
        if "SSE-KMS" in configuration:
            self.evaluated_keys = ['configuration/[0]/SSE-KMS']
            return CheckResult.PASSED
        return CheckResult.FAILED


check = EMRClusterIsEncryptedKMS()
