from __future__ import annotations
from typing import Any
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class ACRGeoreplicated(BaseResourceValueCheck):
    def __init__(self) -> None:

        name = "Ensure geo-replicated container registries to match multi-region container deployments."
        id = "CKV_AZURE_165"
        supported_resources = ("Microsoft.ContainerRegistry/registries/replications",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'location'

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = ACRGeoreplicated()
