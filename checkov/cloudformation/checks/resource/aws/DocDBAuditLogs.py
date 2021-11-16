from typing import Any

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DocDBAuditLogs(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DocDB has audit logs enabled"
        id = "CKV_AWS_104"
        supported_resources = ["AWS::DocDB::DBClusterParameterGroup"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/Parameters/audit_logs"

    def get_expected_value(self) -> Any:
        return "enabled"


check = DocDBAuditLogs()
