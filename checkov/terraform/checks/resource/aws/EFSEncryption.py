from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class EFSEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the EFS is securely encrypted"
        id = "CKV_AWS_41"
        supported_resources = ['aws_efs_file_system']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at cloudtrail:
            https://www.terraform.io/docs/providers/aws/r/cloudtrail.html
        :param conf: efs configuration
        :return: <CheckResult>
        """
        if "kms_key_id" in conf.keys():
            return CheckResult.PASSED
        return CheckResult.FAILED


check = EFSEncryption()
