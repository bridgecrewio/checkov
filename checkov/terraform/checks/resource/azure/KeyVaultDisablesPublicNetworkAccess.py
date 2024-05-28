from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class KeyVaultDisablesPublicNetworkAccess(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Key Vault disables public network access"
        id = "CKV_AZURE_189"
        supported_resources = ('azurerm_key_vault',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "public_network_access_enabled"

    def get_expected_value(self):
        return False

    def scan_resource_conf(self, conf) -> CheckResult:
        """
        KeyVaultDisablesPublicNetworkAccess unique logic.
        public_network_access_enabled default value is True (when creating it)
        If it False - check pass
        Otherwise, we check that ip rules configured inside network_acls.

        """
        conf_value = conf.get(self.get_inspected_key())
        conf_value = conf_value[0] if isinstance(conf_value, list) else conf_value
        if self.get_expected_value() == conf_value:
            return CheckResult.PASSED
        if conf.get("network_acls"):
            network_acls = conf.get("network_acls")
            if isinstance(network_acls, list):
                for network_acl in network_acls:
                    if isinstance(network_acl, dict):
                        ip_rules = network_acl.get("ip_rules")
                        # Get first element in ip_rules (as parser wrap it with list).
                        ip_rules = ip_rules[0] if ip_rules and isinstance(ip_rules, list) else ip_rules
                        if ip_rules:
                            return CheckResult.PASSED

        return CheckResult.FAILED


check = KeyVaultDisablesPublicNetworkAccess()
