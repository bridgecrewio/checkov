from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class CloudtrailLogValidation(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CloudTrail log file validation is enabled"
        id = "CKV_AWS_36"
        supported_resources = ['AWS::CloudTrail::Trail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for log validation configuration at cloudtrail:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html
        :param conf: cloudtrail configuration
        :return: <CheckResult>
        """

        if 'Properties' in conf.keys():
            if 'EnableLogFileValidation' in conf['Properties'].keys():
                if conf['Properties']['EnableLogFileValidation'] == True:
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = CloudtrailLogValidation()
