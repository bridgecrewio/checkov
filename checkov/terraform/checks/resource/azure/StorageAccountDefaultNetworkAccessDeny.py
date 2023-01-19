from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class StorageAccountDefaultNetworkAccessDeny(BaseResourceCheck):
    def __init__(self):
        name = "Ensure default network access rule for Storage Accounts is set to deny"
        id = "CKV_AZURE_35"
        supported_resources = ['azurerm_storage_account', 'azurerm_storage_account_network_rules']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Ensures a storage account is not widely accessible by default, using the default action in network rules
        configuration.
        Network Rules can be defined either directly on the azurerm_storage_account resource,
        or using the azurerm_storage_account_network_rules resource. If the latter is used, the check is skipped for
        the azurerm_storage_account resource (which would return as failed).

        :param default_action:
        :return: Check Result
        """
        network_conf = [conf]
        evaluated_key_prefix = ''
        if 'network_rules' in conf:
            network_conf = conf['network_rules']
            self.evaluated_keys = ['network_rules']
            evaluated_key_prefix = 'network_rules/[0]/'
        if 'default_action' in network_conf[0]:
            self.evaluated_keys = [f'{evaluated_key_prefix}default_action']
            if network_conf[0]['default_action'][0] == 'Deny':
                return CheckResult.PASSED
            return CheckResult.FAILED

        # missing block is valid for storage accounts but not azurerm_storage_account_network_rules
        return CheckResult.UNKNOWN


check = StorageAccountDefaultNetworkAccessDeny()
