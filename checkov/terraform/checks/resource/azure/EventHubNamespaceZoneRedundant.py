from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

LOCATIONS_W_REDUNDANCY = [
    # Asia Pacific
    "Australia East", "australiaeast",
    "Central India", "centralindia",
    "China North 3", "chinanorth3",
    "East Asia", "eastasia",
    "Indonesia Central", "indonesiacentral",
    "Japan East", "japaneast",
    "Japan West", "japanwest",
    "Korea Central", "koreacentral",
    "New Zealand North", "newzealandnorth",
    "South Africa North", "southafricanorth",
    "Southeast Asia", "southeastasia",
    # Canada
    "Canada Central", "canadacentral",
    # Europe
    "France Central", "francecentral",
    "Germany West Central", "germanywestcentral",
    "Italy North", "italynorth",
    "North Europe", "northeurope",
    "Norway East", "norwayeast",
    "Poland Central", "polandcentral",
    "Spain Central", "spaincentral",
    "Sweden Central", "swedencentral",
    "Switzerland North", "switzerlandnorth",
    "UK South", "uksouth",
    "West Europe", "westeurope",
    # Mexico
    "Mexico Central", "mexicocentral",
    # Middle East
    "Israel Central", "israelcentral",
    "Qatar Central", "qatarcentral",
    "UAE North", "uaenorth",
    # South America
    "Brazil South", "brazilsouth",
    # US
    "Central US", "centralus",
    "East US", "eastus",
    "East US 2", "eastus2",
    "South Central US", "southcentralus",
    "US Gov Virginia", "usgovvirginia",
    "West US 2", "westus2",
    "West US 3", "westus3"
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
