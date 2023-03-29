from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CloudWatchLogGroupRetentionYear(BaseResourceCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AU-10, NIST.800-53.r5 AU-11, NIST.800-53.r5 AU-6(3), NIST.800-53.r5 AU-6(4),
        NIST.800-53.r5 CA-7, NIST.800-53.r5 SI-12
        CloudWatch log groups should be retained for at least 1 year
        """
        name = "Ensure that CloudWatch Log Group specifies retention days"
        id = "CKV_AWS_338"
        supported_resource = ['aws_cloudwatch_log_group']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf) -> CheckResult:
        if isinstance(conf.get('retention_in_days'), list) and isinstance(conf.get('retention_in_days')[0], int) \
                and conf.get('retention_in_days')[0] >= 365:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = CloudWatchLogGroupRetentionYear()
