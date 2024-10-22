from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DBInstanceLogging(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 AC-2(4), NIST.800-53.r5 AC-4(26), NIST.800-53.r5 AC-6(9), NIST.800-53.r5 AU-10,
        NIST.800-53.r5 AU-12, NIST.800-53.r5 AU-2, NIST.800-53.r5 AU-3, NIST.800-53.r5 AU-6(3), NIST.800-53.r5 AU-6(4),
        NIST.800-53.r5 CA-7, NIST.800-53.r5 SC-7(10), NIST.800-53.r5 SC-7(9), NIST.800-53.r5 SI-3(8),
        NIST.800-53.r5 SI-4(20), NIST.800-53.r5 SI-7(8)
        Database logging should be enabled
        """
        name = "Ensure that RDS Cluster log capture is enabled"
        id = "CKV_AWS_324"
        supported_resources = ("aws_rds_cluster",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "enabled_cloudwatch_logs_exports/[0]"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = DBInstanceLogging()
