from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from typing import Dict, Any


class KeyVaultDisablesPublicNetworkAccess(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Key Vault disables public network access"
        id = "CKV_AZURE_189"
        supported_resources = ("Microsoft.KeyVault/vaults",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "publicNetworkAccess"

    def get_expected_value(self) -> str:
        return "disabled"

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties = conf.get("properties", {})
        if self.get_inspected_key() in properties:
            conf_value = conf["properties"][self.get_inspected_key()]
            if conf_value and conf_value == self.get_expected_value():
                return CheckResult.PASSED

        if properties and "networkAcls" in properties:
            network_acls = conf["properties"]["networkAcls"]
            if isinstance(network_acls, dict) and "ipRules" in network_acls:
                ip_rules = network_acls["ipRules"]
                ip_rules = ip_rules[0] if ip_rules and isinstance(ip_rules, list) else ip_rules
                if ip_rules:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = KeyVaultDisablesPublicNetworkAccess()
