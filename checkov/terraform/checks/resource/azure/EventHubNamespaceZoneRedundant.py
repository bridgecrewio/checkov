from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

LOCATIONS_W_REDUNDANCY = [
    "Brazil South", "France Central", "Qatar Central", "South Africa North", "Australia East",
    "Canada Central", "Italy North", "UAE North", "Central India",
    "Central US", "Germany West Central", "Israel Central", "Japan East",
    "East US", "Norway East", "Japan West",
    "East US 2", "North Europe", "Southeast Asia",
    "South Central US", "UK South", "East Asia",
    "US Gov Virginia", "West Europe", "China North 3",
    "West US 2", "Sweden Central", "Korea Central",
    "West US 3", "Switzerland North", "New Zealand North",
    "Mexico Central", "Poland Central",
    "Spain Central"
]


class EventHubNamespaceZoneRedundant(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        Zone Redundancy is now determined automatically based on region.
        """
        name = "Ensure the Azure Event Hub Namespace is zone redundant"
        id = "CKV_AZURE_228"
        supported_resources = ("azurerm_eventhub_namespace",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "location"

    def get_expected_values(self):
        return LOCATIONS_W_REDUNDANCY


check = EventHubNamespaceZoneRedundant()
