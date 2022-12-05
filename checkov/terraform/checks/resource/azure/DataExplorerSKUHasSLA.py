from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DataExplorerSKUHasSLA(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that data explorer uses Sku with an SLA"
        id = "CKV_AZURE_180"
        supported_resources = ['azurerm_kusto_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'sku' in conf and conf['sku'][0]:
            sku = conf['sku'][0]
            if 'name' in sku:
                name = sku['name']
                if "No SLA" in name[0]:
                    return CheckResult.FAILED
                return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = DataExplorerSKUHasSLA()
