from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class EFSEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure EFS is securely encrypted"
        id = "CKV_AWS_42"
        supported_resources = ['AWS::EFS::FileSystem']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Looks for encryption configuration at aws_efs_filesystem:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html
        :param conf: aws_efs_filesystem configuration
        :return: <CheckResult>
        """
        if conf.get('Properties'):
            if conf['Properties'].get('Encrypted'):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = EFSEncryption()
