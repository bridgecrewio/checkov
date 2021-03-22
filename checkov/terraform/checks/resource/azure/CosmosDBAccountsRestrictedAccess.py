from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CosmosDBAccountsRestrictedAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Cosmos DB accounts have restricted access"
        id = "CKV_AZURE_99"
        supported_resources = ['azurerm_cosmosdb_account']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'public_network_access_enabled' not in conf or conf['public_network_access_enabled'][0]:
            if 'is_virtual_network_filter_enabled' in conf and conf['is_virtual_network_filter_enabled'][0]:
                if ('virtual_network_rule' in conf and conf['virtual_network_rule'][0]) \
                        or ('ip_range_filter' in conf and conf['ip_range_filter'][0]):
                    return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CosmosDBAccountsRestrictedAccess()
