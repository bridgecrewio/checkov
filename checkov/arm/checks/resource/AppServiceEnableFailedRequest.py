from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AppServiceEnableFailedRequest(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        todo: revisit when graph fully enabled as web config section could be missing entirely from a web app
        """

        name = "Ensure that App service enables failed request tracing"
        id = "CKV_AZURE_66"
        supported_resources = ["Microsoft.Web/sites/config"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/requestTracingEnabled"


check = AppServiceEnableFailedRequest()
