from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ELBwListenerNotTLSSSL(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure AWS Elastic Load Balancer listener uses TLS/SSL"
        id = "CKV_AWS_376"
        supported_resource = ("aws_elb",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if 'listener' in conf:
            for listener in conf.get('listener'):
                if 'instance_protocol' in listener:
                    if listener.get('instance_protocol')[0].lower() in ('http', 'tcp'):
                        return CheckResult.FAILED
                    if listener.get('instance_protocol')[0].lower() in ('https', 'ssl') and \
                            ('ssl_certificate_id' not in listener or listener.get('ssl_certificate_id') == ""):
                        return CheckResult.FAILED

        return CheckResult.PASSED


check = ELBwListenerNotTLSSSL()
