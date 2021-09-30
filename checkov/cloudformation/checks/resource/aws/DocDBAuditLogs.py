from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.parsers.node import dict_node
from checkov.common.models.enums import CheckResult, CheckCategories


class DocDBAuditLogs(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure DocDB has audit logs enabled"
        id = "CKV_AWS_104"
        supported_resources = ["AWS::DocDB::DBClusterParameterGroup"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict_node) -> CheckResult:
        params = conf.get("Properties", {}).get("Parameters", {})

        if params.get("audit_logs") == "enabled":
            return CheckResult.PASSED

        return CheckResult.FAILED


check = DocDBAuditLogs()
