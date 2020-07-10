from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class cloudwatchLogGroupRetention(BaseResourceCheck):
    def __init__(self):
        name = "Ensure cloudwatch log groups specify retention days"
        id = "CKV_AWS_66"
        supported_resource = ['AWS::Logs::LogGroup']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf):
        """
            Looks for retention days in cloudwatch log group :
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html#cfn-cwl-loggroup-retentionindays
        :param conf: AWS::Logs::LogGroup configuration
        :return: <CheckResult>
        """

        if 'Properties' in conf.keys():
            if 'RetentionInDays' in conf['Properties'].keys():
                return CheckResult.PASSED
        return CheckResult.FAILED


check = cloudwatchLogGroupRetention()
