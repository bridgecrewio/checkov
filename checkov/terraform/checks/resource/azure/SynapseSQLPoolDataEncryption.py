from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SynapseSQLPoolDataEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Synapse SQL pools are encrypted"
        id = "CKV_AZURE_241"
        supported_resources = ['azurerm_synapse_sql_pool']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'data_encrypted' in conf and conf['data_encrypted'][0] is True:
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['data_encrypted']


check = SynapseSQLPoolDataEncryption()
