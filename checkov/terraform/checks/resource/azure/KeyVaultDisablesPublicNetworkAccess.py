from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class KeyVaultDisablesPublicNetworkAccess(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that key vault disable public network access"
        id = "CKV_AZURE_189"
        supported_resources = ['azurerm_key_vault']
        categories = [CheckCategories.NETWORKING]
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
        Otherwise, we check that network_acls configure exists.

        """
        network_acls_key = "network_acls"
        if self.get_inspected_key() in conf:
            conf_value = conf.get(self.get_inspected_key())
            conf_value = conf_value[0] if isinstance(conf_value, list) else conf_value
            if self.get_expected_value() == conf_value:
                return CheckResult.PASSED
        if conf.get(network_acls_key):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = KeyVaultDisablesPublicNetworkAccess()
