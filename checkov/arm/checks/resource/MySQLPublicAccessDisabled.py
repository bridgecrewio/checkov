from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class MySQLPublicAccessDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure 'public network access enabled' is set to 'False' for mySQL servers"
        id = "CKV_AZURE_53"
        supported_resources = ("Microsoft.DBforMySQL/servers",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/publicNetworkAccess"

    def get_expected_value(self) -> str:
        """
        Returns the default expected value, governed by provider best practices
        """
        return "False"


check = MySQLPublicAccessDisabled()
