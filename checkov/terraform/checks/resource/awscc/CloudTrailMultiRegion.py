from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudTrailMultiRegion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure CloudTrail is enabled in all regions"
        id = "CKV_AWS_67"
        supported_resources = ("awscc_cloudtrail_trail",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "is_multi_region_trail"

    def get_expected_value(self):
        return True


check = CloudTrailMultiRegion()
