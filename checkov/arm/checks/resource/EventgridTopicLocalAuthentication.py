from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class EventgridTopicLocalAuthentication(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Event Grid Topic local Authentication is disabled"
        id = "CKV_AZURE_192"
        supported_resources = ("Microsoft.EventGrid/topics",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/disableLocalAuth"

    def get_expected_value(self) -> bool:
        return True


check = EventgridTopicLocalAuthentication()
