from typing import Any, Dict
import re

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

_SECURE_RE = re.compile(r"^TLSv1\.(?:2|3)_\d{4}$")


class CloudFrontTLS12(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Verify CloudFront Distribution Viewer Certificate is using TLS v1.2 or higher"
        id = "CKV_AWS_174"
        supported_resources = ("aws_cloudfront_distribution",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        # keep this for reporting
        return "viewer_certificate/[0]/minimum_protocol_version"

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        vc_list = conf.get("viewer_certificate")
        if not isinstance(vc_list, list) or not vc_list or not isinstance(vc_list[0], dict):
            return CheckResult.FAILED

        vc = vc_list[0]

        default_cert = vc.get("cloudfront_default_certificate")
        if isinstance(default_cert, list):
            default_cert = default_cert[0] if default_cert else None
        if isinstance(default_cert, str):
            default_cert = default_cert.lower() == "true"
        if default_cert is True:
            return CheckResult.FAILED

        mpv = vc.get("minimum_protocol_version")
        if isinstance(mpv, list):
            mpv = mpv[0] if mpv else None
        if isinstance(mpv, str) and _SECURE_RE.match(mpv):
            return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self):
        return [self.get_inspected_key()]


check = CloudFrontTLS12()
