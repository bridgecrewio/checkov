from typing import Any, Dict
import re

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult

_SECURE_RE = re.compile(r"^TLSv1\.(?:2|3)_\d{4}$")


class CloudFrontTLS12(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Verify CloudFront Distribution Viewer Certificate is using TLS v1.2 or higher"
        id = "CKV_AWS_174"
        supported_resources = ["AWS::CloudFront::Distribution"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/DistributionConfig/ViewerCertificate/MinimumProtocolVersion"

    @staticmethod
    def validate_value(value: Any) -> bool:
        return isinstance(value, str) and bool(_SECURE_RE.match(value))

    def get_evaluated_keys(self):
        return [self.get_inspected_key()]

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        # Navigate CFN structure safely
        props = conf.get("Properties")
        if not isinstance(props, dict):
            return CheckResult.FAILED

        dist_cfg = props.get("DistributionConfig")
        if not isinstance(dist_cfg, dict):
            return CheckResult.FAILED

        viewer_cert = dist_cfg.get("ViewerCertificate")
        if not isinstance(viewer_cert, dict):
            return CheckResult.FAILED

        # If they use the CloudFront default cert, you can't set a secure policy -> fail explicitly
        if viewer_cert.get("CloudFrontDefaultCertificate") is True:
            return CheckResult.FAILED

        mpv = viewer_cert.get("MinimumProtocolVersion")
        if isinstance(mpv, str) and _SECURE_RE.match(mpv):
            return CheckResult.PASSED

        return CheckResult.FAILED


check = CloudFrontTLS12()
