from typing import Any, Dict, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MySQLPublicAccessDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure 'public network access enabled' is set to 'False' for mySQL servers"
        id = "CKV_AZURE_53"
        supported_resources = ("azurerm_mysql_server", "azurerm_mysql_flexible_server",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if self.entity_type == "azurerm_mysql_flexible_server":
            # On a flexible server `public_network_access_enabled` is computed and
            # cannot be set. Public access is set with `public_network_access`, and
            # is disabled automatically with VNet integration (`delegated_subnet_id`).
            self.evaluated_keys = ["public_network_access", "delegated_subnet_id"]
            access = conf.get("public_network_access")
            if access:
                if self._is_variable_dependant(access[0]):
                    return CheckResult.UNKNOWN
                return CheckResult.PASSED if access[0] == "Disabled" else CheckResult.FAILED
            if conf.get("delegated_subnet_id") and conf["delegated_subnet_id"][0]:
                return CheckResult.PASSED
            return CheckResult.FAILED
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "public_network_access_enabled"

    def get_expected_value(self) -> Any:
        """
        Returns the default expected value, governed by provider best practices
        """
        return False


check = MySQLPublicAccessDisabled()
