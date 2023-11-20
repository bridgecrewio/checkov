from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class APIServicesUseVirtualNetwork(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that API management services use virtual networks"
        id = "CKV_AZURE_107"
        supported_resources = ("Microsoft.ApiManagement/service",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.FAILED,
        )

    def get_inspected_key(self) -> str:
        return "properties/virtualNetworkConfiguration"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = APIServicesUseVirtualNetwork()
