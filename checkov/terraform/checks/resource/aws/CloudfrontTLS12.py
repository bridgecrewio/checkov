from typing import List, Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudFrontTLS12(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Verify CloudFront Distribution Viewer Certificate is using TLS v1.2"
        id = "CKV_AWS_174"
        supported_resources = ("aws_cloudfront_distribution",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "viewer_certificate/[0]/minimum_protocol_version"

    def get_expected_values(self) -> List[Any]:
        return ["TLSv1.2_2018", "TLSv1.2_2019", "TLSv1.2_2021"]

    def get_expected_value(self) -> Any:
        return "TLSv1.2_2021"


check = CloudFrontTLS12()
