from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class CloudtrailMultiRegion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure CloudTrail is enabled in all Regions"
        id = "CKV_AWS_67"
        supported_resources = ['aws_cloudtrail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "is_multi_region_trail"


check = CloudtrailMultiRegion()
