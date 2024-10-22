from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck

SUPPORTED_ENGINES = {"aurora", "aurora-mysql"}


class RDSClusterAuroraBacktrack(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 CP-10, NIST.800-53.r5 CP-6, NIST.800-53.r5 CP-6(1), NIST.800-53.r5 CP-6(2), NIST.800-53.r5 CP-9,
        NIST.800-53.r5 SI-13(5)	Amazon Aurora clusters should have backtracking enabled
        """
        name = "Ensure that RDS Aurora Clusters have backtracking enabled"
        id = "CKV_AWS_326"
        supported_resources = ("aws_rds_cluster",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_attribute_result=CheckResult.FAILED,
        )

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        engine = conf.get("engine")
        if engine and isinstance(engine, list) and engine[0] not in SUPPORTED_ENGINES:
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf=conf)

    def get_inspected_key(self) -> str:
        return "backtrack_window"

    def get_forbidden_values(self) -> list[Any]:
        return [0]


check = RDSClusterAuroraBacktrack()
