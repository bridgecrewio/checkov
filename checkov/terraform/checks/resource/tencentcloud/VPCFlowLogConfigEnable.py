from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import \
    BaseResourceNegativeValueCheck


class VPCFlowLogConfigEnable(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud VPC flow logs are enabled"
        id = "CKV_TC_14"
        supported_resources = ['tencentcloud_vpc_flow_log_config']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'enable/[0]'

    def get_forbidden_values(self) -> List[Any]:
        return [False]


check = VPCFlowLogConfigEnable()
