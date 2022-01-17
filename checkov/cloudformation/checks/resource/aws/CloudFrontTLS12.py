from typing import Any, List

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class CloudFrontTLS12(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Verify CloudFront Distribution Viewer Certificate is using TLS v1.2"
        id = "CKV_AWS_174"
        supported_resources = ["AWS::CloudFront::Distribution"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/DistributionConfig/ViewerCertificate/MinimumProtocolVersion"

    def get_expected_values(self) -> List[str]:
        return ['TLSv1.2_2018', 'TLSv1.2_2019', 'TLSv1.2_2021']

    def get_expected_value(self) -> Any:
        return 'TLSv1.2_2021'


check = CloudFrontTLS12()
