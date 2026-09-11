from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ELBv2TargetGroupHealthCheckProtocol(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure ELBv2 target group health check uses HTTPS"
        id = "CKV_AWS_394"
        supported_resources = ["aws_lb_target_group", "aws_alb_target_group"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Skip if target_type is lambda (no health checks apply)
        target_type = conf.get("target_type")
        if target_type:
            if isinstance(target_type, list):
                target_type = target_type[0]
            if target_type == "lambda":
                return CheckResult.PASSED

        # Skip if transport protocol is TCP, UDP, TCP_UDP, or GENEVE
        # (these protocols cannot use HTTPS health checks)
        protocol = conf.get("protocol")
        if protocol:
            if isinstance(protocol, list):
                protocol = protocol[0]
            if isinstance(protocol, str) and protocol.upper() in ("TCP", "UDP", "TCP_UDP", "GENEVE"):
                return CheckResult.PASSED

        # Check health_check block
        self.evaluated_keys = ["health_check/[0]/protocol"]
        health_check = conf.get("health_check")
        if health_check:
            if isinstance(health_check, list):
                health_check = health_check[0]
            if isinstance(health_check, dict):
                hc_protocol = health_check.get("protocol")
                if hc_protocol:
                    if isinstance(hc_protocol, list):
                        hc_protocol = hc_protocol[0]
                    if BaseResourceCheck._is_variable_dependant(hc_protocol):
                        return CheckResult.UNKNOWN
                    if isinstance(hc_protocol, str) and hc_protocol.upper() == "HTTPS":
                        return CheckResult.PASSED

        # FAIL if health_check block is absent or protocol is not HTTPS
        return CheckResult.FAILED


check = ELBv2TargetGroupHealthCheckProtocol()
