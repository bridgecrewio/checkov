from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class KMSRotation(BaseResourceCheck):
    def __init__(self):
        name = "Ensure rotation for customer created CMKs is enabled"
        id = "CKV_AWS_7"
        supported_resources = ['AWS::KMS::Key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Looks for key rotation configuration of an AWS KMS key
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html
        :param conf: aws_kms_key
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if conf['Properties'].get('EnableKeyRotation'):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = KMSRotation()
