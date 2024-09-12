from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class CloudFrontGeoRestrictionDisabled(BaseResourceNegativeValueCheck):

    def __init__(self) -> None:
        name = "Ensure AWS CloudFront web distribution has geo restriction enabled"
        id = "CKV_AWS_374"
        supported_resources = ('aws_cloudfront_distribution',)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "restrictions/[0]/geo_restriction/[0]/restriction_type"

    def get_forbidden_values(self) -> list:
        return ["none"]


check = CloudFrontGeoRestrictionDisabled()
