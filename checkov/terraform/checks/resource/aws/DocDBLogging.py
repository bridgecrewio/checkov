from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class DocDBLogging(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DocDB Logging is enabled"
        id = "CKV_AWS_85"
        supported_resources = ['aws_docdb_cluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        log_types = ["profiler", "audit"]

        if 'enabled_cloudwatch_logs_exports' in conf:
            if all(elem in conf["enabled_cloudwatch_logs_exports"][0] for elem in log_types):
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        return CheckResult.FAILED


check = DocDBLogging()
