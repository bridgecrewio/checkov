from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureDefenderOnSqlServers(BaseResourceCheck):

    def __init__(self):
        name = "Ensure that Azure Defender is set to On for Azure SQL database servers"
        id = "CKV_AZURE_69"
        supported_resources = ['azurerm_security_center_subscription_pricing']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        return CheckResult.PASSED if conf.get('resource_type', [None])[0] != 'SqlServers' \
                                     or conf.get('tier', [None])[0] == 'Standard' else CheckResult.FAILED


check = AzureDefenderOnSqlServers()
