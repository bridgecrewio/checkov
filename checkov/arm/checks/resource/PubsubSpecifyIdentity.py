from typing import Any

from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class PubsubSpecifyIdentity(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Web PubSub uses managed identities to access Azure resources"
        id = "CKV_AZURE_176"
        supported_resources = ["Microsoft.SignalRService/webPubSub"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "identity/type"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = PubsubSpecifyIdentity()
