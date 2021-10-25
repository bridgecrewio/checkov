from checkov.common.parsers.node import DictNode
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RDSIAMAuthentication(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure RDS database has IAM authentication enabled"
        id = "CKV_AWS_161"
        supported_resources = ["AWS::RDS::DBInstance"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/EnableIAMDatabaseAuthentication"

    def scan_resource_conf(self, conf: DictNode) -> CheckResult:
        # IAM authentication is only supported for MySQL and PostgreSQL
        engine = conf.get("Properties", {}).get("Engine", {})
        if engine not in ("mysql", "postgres"):
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)


check = RDSIAMAuthentication()
