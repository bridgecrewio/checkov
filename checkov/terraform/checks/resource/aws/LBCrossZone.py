from typing import Dict, List

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class LBCrossZone(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Load Balancer (Network/Gateway) has cross-zone load balancing enabled"
        id = "CKV_AWS_152"
        supported_resources = ["aws_lb", "aws_alb"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List]) -> CheckResult:
        if conf.get("load_balancer_type", ["application"]) == ["application"]:
            return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "enable_cross_zone_load_balancing"


check = LBCrossZone()
