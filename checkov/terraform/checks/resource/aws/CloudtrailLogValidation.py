from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class CloudtrailLogValidation(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CloudTrail log file validation is enabled"
        id = "CKV_AWS_36"
        supported_resources = ['aws_cloudtrail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for log validation configuration at cloudtrail:
            https://www.terraform.io/docs/providers/aws/r/cloudtrail.html
        :param conf: cloudtrail configuration
        :return: <CheckResult>
        """
        if "enable_log_file_validation" in conf.keys():
            if conf["enable_log_file_validation"][0] == True:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = CloudtrailLogValidation()
