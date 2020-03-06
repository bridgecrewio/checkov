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
            Looks for encryption configuration in RFS:
            https://www.terraform.io/docs/providers/aws/r/efs_file_system.html
        :param conf: aws_efs_file_system configuration
        :return: <CheckResult>
        """
        if "encrypted" in conf.keys():
            if conf["encrypted"][0] == True:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = EFSEncryption()
