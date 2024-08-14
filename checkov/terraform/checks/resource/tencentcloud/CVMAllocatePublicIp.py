from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import \
    BaseResourceNegativeValueCheck


class CVMAllocatePublicIp(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud CVM instance does not allocate a public IP"
        id = "CKV_TC_2"
        supported_resources = ['tencentcloud_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'allocate_public_ip/[0]'

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = CVMAllocatePublicIp()
