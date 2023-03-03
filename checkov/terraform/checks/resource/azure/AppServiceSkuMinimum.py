from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class AppServiceSkuMinimum(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        # "Azure App Services provide a range of different plans that can be used to scale your application.
        # Each plan provides different levels of performance and features.
        # To get you started a number of entry level plans are available.
        # The Free, Shared, and Basic plans can be used for limited testing and development.
        # These plans are not suitable for production use.
        # Production workloads are best suited to standard and premium plans with PremiumV3 the newest plan."
        name = "Ensure App Service plan suitable for production use"
        id = "CKV_AZURE_211"
        supported_resources = ['azurerm_service_plan']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'sku_name'

    def get_forbidden_values(self) -> list[Any]:
        return ["B1", "B2", "B3", "F1", "D1"]


check = AppServiceSkuMinimum()
