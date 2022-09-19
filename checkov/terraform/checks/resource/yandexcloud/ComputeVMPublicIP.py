from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class ComputeVMPublicIP(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure compute instance does not have public IP."
        id = "CKV_YC_2"
        categories = (CheckCategories.NETWORKING,)
        supported_resources = ("yandex_compute_instance",)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "network_interface/[0]/nat"

    def get_forbidden_values(self) -> list[Any]:
        return [True]


check = ComputeVMPublicIP()
