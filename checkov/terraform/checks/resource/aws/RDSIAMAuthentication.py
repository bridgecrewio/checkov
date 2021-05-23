from typing import Dict, List, Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class RDSIAMAuthentication(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure RDS database has IAM authentication enabled"
        id = "CKV_AWS_161"
        supported_resources = ["aws_db_instance"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "iam_database_authentication_enabled"

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        # IAM authentication is only supported for MySQL and PostgreSQL
        if conf.get("engine") not in (["mysql"], ["postgres"]):
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)


check = RDSIAMAuthentication()
