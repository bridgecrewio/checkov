from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudtrailMultiRegion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure CloudTrail is enabled in all Regions"
        id = "CKV_AWS_67"
        supported_resources = ['AWS::CloudTrail::Trail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/IsMultiRegionTrail'


check = CloudtrailMultiRegion()
