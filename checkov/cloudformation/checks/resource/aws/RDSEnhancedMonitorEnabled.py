from __future__ import annotations

from typing import Any

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class RDSEnhancedMonitorEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that enhanced monitoring is enabled for Amazon RDS instances"
        id = "CKV_AWS_118"
        supported_resources = ("AWS::RDS::DBInstance",)  # AWS::RDS::DBCluster doesn't support this config
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/MonitoringInterval"

    def get_expected_values(self) -> list[Any]:
        # supports int and str
        return [1, 5, 10, 15, 30, 60, "1", "5", "10", "15", "30", "60"]


check = RDSEnhancedMonitorEnabled()
