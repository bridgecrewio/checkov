from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_int
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CloudFrontResponseHeaderStrictTransportSecurity(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure CloudFront response header policy enforces Strict Transport Security"
        id = "CKV_AWS_259"
        supported_resources = ("aws_cloudfront_response_headers_policy",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security

        self.evaluated_keys = ["security_headers_config"]
        security_headers = conf.get("security_headers_config")
        if security_headers and isinstance(security_headers, list):
            self.evaluated_keys = ["security_headers_config/[0]/strict_transport_security"]
            sts = security_headers[0].get("strict_transport_security")
            if sts and isinstance(sts, list):
                # if one of those configs is not set correctly, then the check should fail
                self.evaluated_keys = [
                    "security_headers_config/[0]/strict_transport_security/[0]/access_control_max_age_sec"
                ]
                max_age = sts[0].get("access_control_max_age_sec")
                if not max_age:
                    return CheckResult.FAILED
                else:
                    max_age_int = force_int(max_age[0])
                    if not max_age_int or max_age_int < 31536000:  # 1 year
                        return CheckResult.FAILED

                self.evaluated_keys.append(
                    "security_headers_config/[0]/strict_transport_security/[0]/include_subdomains"
                )
                subdomains = sts[0].get("include_subdomains")
                if not subdomains or not subdomains[0]:
                    return CheckResult.FAILED

                self.evaluated_keys.append("security_headers_config/[0]/strict_transport_security/[0]/preload")
                preload = sts[0].get("preload")
                if not preload or not preload[0]:
                    return CheckResult.FAILED

                self.evaluated_keys.append("security_headers_config/[0]/strict_transport_security/[0]/override")
                override = sts[0].get("override")
                if not override or not override[0]:
                    return CheckResult.FAILED

                return CheckResult.PASSED

        return CheckResult.FAILED


check = CloudFrontResponseHeaderStrictTransportSecurity()
