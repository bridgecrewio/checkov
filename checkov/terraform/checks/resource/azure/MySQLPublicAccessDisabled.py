from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MySQLPublicAccessDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure 'public network access enabled' is set to 'False' for mySQL servers"
        id = "CKV_AZURE_53"
        supported_resources = ("azurerm_mysql_server",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_network_access_enabled"

    def get_expected_value(self) -> Any:
        """
        Returns the default expected value, governed by provider best practices
        """
        return False


check = MySQLPublicAccessDisabled()
