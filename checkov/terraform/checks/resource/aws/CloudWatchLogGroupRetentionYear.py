from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import \
    BaseResourceCheck


class CloudWatchLogGroupRetentionYear(BaseResourceCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 AU-10, NIST.800-53.r5 AU-11, NIST.800-53.r5 AU-6(3), NIST.800-53.r5 AU-6(4),
        NIST.800-53.r5 CA-7, NIST.800-53.r5 SI-12
        CloudWatch log groups should be retained for at least 1 year
        """
        name = "Ensure CloudWatch log groups retains logs for at least 1 year"
        id = "CKV_AWS_338"
        supported_resource = ("aws_cloudwatch_log_group",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        retention = conf.get("retention_in_days")
        if retention and isinstance(retention, list):
            retention = retention[0]
            if not isinstance(retention, int):
                # probably a dependent variable
                return CheckResult.UNKNOWN
            # If you select 0, the events in the log group are always retained and never expire.
            if retention == 0 or retention >= 365:
                return CheckResult.PASSED

        return CheckResult.FAILED


check = CloudWatchLogGroupRetentionYear()
