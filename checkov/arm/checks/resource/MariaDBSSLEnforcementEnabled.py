from typing import Any

from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class MariaDBSSLEnforcementEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure 'Enforce SSL connection' is set to 'ENABLED' for MariaDB servers"
        id = "CKV_AZURE_47"
        supported_resources = ["Microsoft.DBforMariaDB/servers"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/sslEnforcement"

    def get_expected_value(self) -> Any:
        return "Enabled"


check = MariaDBSSLEnforcementEnabled()
