from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class ELBCrossZoneEnable(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that ELB is cross-zone-load-balancing enabled"
        id = "CKV_AWS_138"
        supported_resources = ['aws_elb']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'cross_zone_load_balancing'


check = ELBCrossZoneEnable()
