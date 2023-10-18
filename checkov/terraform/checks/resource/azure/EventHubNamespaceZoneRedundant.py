from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class EventHubNamespaceZoneRedundant(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        This is a best practice as the all-active Azure Event Hubs cluster model with availability zone support provides
        resiliency against grave hardware failures and even catastrophic loss of entire datacenter facilities.
        If an Event Hubs namespace is created in a region with availability zones,
        the outage risk is further spread across three physically separated facilities, and the service has enough
        capacity reserves to instantly cope up with the complete, catastrophic loss of the entire facility.

        When a client application sends events to an Event Hubs without specifying a partition, events are automatically
        distributed among partitions in the event hub. If a partition isn't available for some reason, events are
        distributed among the remaining partitions. This behavior allows for the greatest amount of up time.
        """
        name = "Ensure the Azure Event Hub Namespace is zone redundant"
        id = "CKV_AZURE_228"
        supported_resources = ("azurerm_eventhub_namespace",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "zone_redundant"


check = EventHubNamespaceZoneRedundant()
