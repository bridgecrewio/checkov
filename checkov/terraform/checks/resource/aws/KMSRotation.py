from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class KMSRotation(BaseResourceCheck):
    def __init__(self):
        name = "Ensure rotation for customer created CMKs is enabled"
        id = "CKV_AWS_7"
        supported_resources = ['aws_kms_key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            validates kms rotation
            https://www.terraform.io/docs/providers/aws/r/kms_key.html
        :param conf: aws_kms_key configuration
        :return: <CheckResult>
        """
        key = 'enable_key_rotation'
        if key in conf.keys():
            if conf[key]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = KMSRotation()
