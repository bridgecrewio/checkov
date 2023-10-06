from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServicePlanZoneRedundant(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        To enhance the resiliency and reliability of business-critical workloads,
        it's recommended to deploy new App Service Plans with zone-redundancy.

        There's no additional cost associated with enabling availability zones.
        Pricing for a zone redundant App Service is the same as a single zone App Service.
        """
        name = "Ensure the App Service Plan is zone redundant"
        id = "CKV_AZURE_225"
        supported_resources = ("azurerm_service_plan",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "zone_balancing_enabled"


check = AppServicePlanZoneRedundant()
