from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class Route53TransferLock(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Route 53 domains have transfer lock protection"
        id = "CKV_AWS_377"
        supported_resources = ('aws_route53domains_registered_domain',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'transfer_lock'

    def get_forbidden_values(self) -> List[Any]:
        return [False]


check = Route53TransferLock()
