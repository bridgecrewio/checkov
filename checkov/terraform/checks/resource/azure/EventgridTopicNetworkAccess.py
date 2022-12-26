from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class EventgridTopicNetworkAccess(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure public network access is disabled for Azure Event Grid Topic"
        id = "CKV_AZURE_193"
        supported_resources = ("azurerm_eventgrid_topic",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_network_access_enabled"

    def get_expected_value(self) -> Any:
        return False


check = EventgridTopicNetworkAccess()
