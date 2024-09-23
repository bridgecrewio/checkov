from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class LBTargetGroup(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure AWS Load Balancer doesn't use HTTP protocol"
        id = "CKV_AWS_378"
        supported_resources = ('aws_lb_target_group', 'aws_alb_target_group',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'protocol'

    def get_forbidden_values(self) -> List[Any]:
        return ["HTTP"]


check = LBTargetGroup()
