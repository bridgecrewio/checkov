from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import Any, List


class ECSClusterLoggingEnabled(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure ECS Cluster enables logging of ECS Exec"
        id = "CKV_AWS_223"
        supported_resources = ["aws_ecs_cluster"]
        categories = [CheckCategories.LOGGING]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "configuration/[0]/execute_command_configuration/[0]/logging"

    def get_forbidden_values(self) -> List[Any]:
        return ["NONE"]


check = ECSClusterLoggingEnabled()
