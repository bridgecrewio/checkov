from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class EFSEncryptionEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure EFS is securely encrypted"
        id = "CKV_AWS_42"
        supported_resources = ['aws_efs_file_system']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at EFS:
            https://www.terraform.io/docs/providers/aws/r/efs_file_system.html
        :param conf: efs configuration
        :return: <CheckResult>
        """
        if "encrypted" in conf.keys():
            return CheckResult.PASSED
        return CheckResult.FAILED


check = EFSEncryptionEnabled()
