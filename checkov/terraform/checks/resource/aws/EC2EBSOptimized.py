from __future__ import annotations

import re
from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

# Instance families where EBS optimization is not enabled by default (previous generation).
# Every other instance type has EBS optimization enabled by default and it cannot be disabled,
# so `ebs_optimized` has no effect for them.
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-optimized.html
NOT_EBS_OPTIMIZED_BY_DEFAULT_FAMILIES = {"c1", "c3", "i2", "m1", "m2", "m3", "r3", "t1", "t2"}
INSTANCE_TYPE_PATTERN = re.compile(r"^([a-z][a-z0-9-]*)\.[a-z0-9]+$")


class EC2EBSOptimized(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that EC2 is EBS optimized"
        id = "CKV_AWS_135"
        supported_resources = ("aws_instance",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        instance_type = conf.get("instance_type")
        if instance_type and isinstance(instance_type, list) and isinstance(instance_type[0], str):
            match = INSTANCE_TYPE_PATTERN.match(instance_type[0])
            if match and match.group(1) not in NOT_EBS_OPTIMIZED_BY_DEFAULT_FAMILIES:
                return CheckResult.PASSED
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "ebs_optimized"

    def get_evaluated_keys(self) -> list[str]:
        return ["instance_type", "ebs_optimized"]


check = EC2EBSOptimized()
