from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3AccessLogs(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the S3 bucket has access logging enabled"
        id = "CKV_AWS_18"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for logging configuration at aws_s3_bucket:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <CheckResult>
        """
        if 'logging' in conf.keys():
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


check = S3AccessLogs()
