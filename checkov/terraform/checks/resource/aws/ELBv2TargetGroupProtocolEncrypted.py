from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ELBv2TargetGroupProtocolEncrypted(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure ELBv2 target group uses an encrypted protocol (HTTPS or TLS)"
        id = "CKV_AWS_395"
        supported_resources = ["aws_lb_target_group", "aws_alb_target_group"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Skip if target_type is lambda (no transport protocol)
        target_type = conf.get("target_type")
        if target_type:
            if isinstance(target_type, list):
                target_type = target_type[0]
            if target_type == "lambda":
                return CheckResult.PASSED

        self.evaluated_keys = ["protocol"]
        protocol = conf.get("protocol")
        if protocol:
            if isinstance(protocol, list):
                protocol = protocol[0]
            if BaseResourceCheck._is_variable_dependant(protocol):
                return CheckResult.UNKNOWN
            if isinstance(protocol, str) and protocol.upper() in ("HTTPS", "TLS"):
                return CheckResult.PASSED

        # FAIL for HTTP, TCP, UDP, TCP_UDP, GENEVE, or missing protocol (defaults to HTTP)
        return CheckResult.FAILED


check = ELBv2TargetGroupProtocolEncrypted()
