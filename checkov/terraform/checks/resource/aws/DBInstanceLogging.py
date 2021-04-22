from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DBInstanceLogging(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that respective logs of Amazon Relational Database Service (Amazon RDS) are enabled"
        id = "CKV_AWS_129"
        supported_resources = ["aws_db_instance"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # which log types are chooseable depends on the engine and engine version and even region,
        # therefore it is only checked, if something is enabled.
        if conf.get("enabled_cloudwatch_logs_exports", [[]])[0]:
            return CheckResult.PASSED

        return CheckResult.FAILED


check = DBInstanceLogging()
