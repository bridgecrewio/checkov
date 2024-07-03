from typing import Any

from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppServicePublicAccessDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Web App public network access is disabled"
        id = "CKV_AZURE_222"
        supported_resources = [
            "Microsoft.Web/sites",
            "Microsoft.Web/sites/slots",
            "Microsoft.Web/sites/config"
        ]
        categories = [CheckCategories.NETWORKING,]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/publicNetworkAccess"

    def get_expected_value(self) -> Any:
        return "Disabled"


check = AppServicePublicAccessDisabled()
