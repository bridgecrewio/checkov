from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import \
    BaseResourceNegativeValueCheck


class CLBListenerProtocol(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud CLBs use modern, encrypted protocols"
        id = "CKV_TC_12"
        supported_resources = ['tencentcloud_clb_listener']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'protocol/[0]'

    def get_forbidden_values(self) -> List[Any]:
        return ["TCP", "UDP", "HTTP"]


check = CLBListenerProtocol()
