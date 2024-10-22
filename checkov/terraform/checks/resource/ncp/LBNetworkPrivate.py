from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class LBNetworkPrivate(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Load Balancer isn't exposed to the internet"
        id = "CKV_NCP_16"
        supported_resources = ("ncloud_lb",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "network_type"

    def get_expected_value(self) -> Any:
        return "PRIVATE"


check = LBNetworkPrivate()
