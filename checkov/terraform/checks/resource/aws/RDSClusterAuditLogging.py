from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

SUPPORTED_ENGINES = {
    "aurora",
    "aurora-mysql",
    "mysql"
}


class RDSClusterAuditLogging(BaseResourceCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 AC-2(4), NIST.800-53.r5 AC-4(26), NIST.800-53.r5 AC-6(9), NIST.800-53.r5 AU-10,
        NIST.800-53.r5 AU-12, NIST.800-53.r5 AU-2, NIST.800-53.r5 AU-3, NIST.800-53.r5 AU-6(3), NIST.800-53.r5 AU-6(4),
        NIST.800-53.r5 CA-7, NIST.800-53.r5 SC-7(10), NIST.800-53.r5 SC-7(9), NIST.800-53.r5 SI-3(8),
        NIST.800-53.r5 SI-4(20), NIST.800-53.r5 SI-7(8)
        Database logging should be enabled
        """
        name = "Ensure that RDS Cluster audit logging is enabled for MySQL engine"
        id = "CKV_AWS_325"
        supported_resources = ("aws_rds_cluster",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        engine = conf.get("engine")
        if engine and isinstance(engine, list) and engine[0] not in SUPPORTED_ENGINES:
            # only MySQL cluster support easy audit logging export
            return CheckResult.UNKNOWN

        logs_exports = conf.get("enabled_cloudwatch_logs_exports")
        if (
            logs_exports
            and isinstance(logs_exports, list)
            and isinstance(logs_exports[0], list)
            and "audit" in logs_exports[0]
        ):
            return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["enabled_cloudwatch_logs_exports"]


check = RDSClusterAuditLogging()
