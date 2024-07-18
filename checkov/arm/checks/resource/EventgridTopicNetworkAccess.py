from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class EventgridTopicNetworkAccess(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure public network access is disabled for Azure Event Grid Topic"
        id = "CKV_AZURE_193"
        supported_resources = ("Microsoft.EventGrid/topics",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/publicNetworkAccess"

    def get_expected_value(self) -> str:
        return "Disabled"


check = EventgridTopicNetworkAccess()
