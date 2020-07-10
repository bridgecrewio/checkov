from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class S3AccessLogs(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the S3 bucket has access logging enabled"
        id = "CKV_AWS_18"
        supported_resources = ['AWS::S3::Bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('Properties') and conf['Properties'].get('LoggingConfiguration') is not None:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = S3AccessLogs()
