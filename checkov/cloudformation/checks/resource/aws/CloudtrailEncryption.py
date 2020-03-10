from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class CloudtrailEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CloudTrail logs are encrypted at rest using KMS CMKs"
        id = "CKV_AWS_35"
        supported_resources = ['AWS::CloudTrail::Trail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at cloudtrail:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html
        :param conf: cloudtrail configuration
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if 'KMSKeyId' in conf['Properties'].keys():
                return CheckResult.PASSED
        return CheckResult.FAILED

check = CloudtrailEncryption()
