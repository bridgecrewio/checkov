from typing import Any, Dict
import re

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

_SECURE_RE = re.compile(r"^TLSv1\.(?:2|3)_\d{4}$")


def _first(v: Any) -> Any:
    # Terraform parser often wraps scalars in single-item lists
    if isinstance(v, list):
        return v[0] if v else None
    return v


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

        # If default CloudFront cert is used -> fail
        default_cert = _first(vc.get("cloudfront_default_certificate"))
        if default_cert in (True, "true"):
            return CheckResult.FAILED

        mpv = _first(vc.get("minimum_protocol_version"))
        if isinstance(mpv, str) and _SECURE_RE.match(mpv):
            return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self):
        return [self.get_inspected_key()]


check = CloudFrontTLS12()
