from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CloudtrailEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CloudTrail logs are encrypted at rest using KMS CMKs"
        id = "CKV_AWS_35"
        supported_resources = ['aws_cloudtrail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at cloudtrail:
            https://www.terraform.io/docs/providers/aws/r/cloudtrail.html
        :param conf: cloudtrail configuration
        :return: <CheckResult>
        """
        if "kms_key_id" in conf.keys():
            return CheckResult.PASSED
        return CheckResult.FAILED


check = CloudtrailEncryption()
