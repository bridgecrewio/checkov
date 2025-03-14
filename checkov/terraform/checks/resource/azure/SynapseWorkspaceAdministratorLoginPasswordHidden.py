from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SynapseWorkspaceAdministratorLoginPasswordHidden(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Synapse Workspace administrator login password is not exposed"
        id = "CKV_AZURE_239"
        supported_resources = ['azurerm_synapse_workspace']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if 'sql_administrator_login_password' in conf:
            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['sql_administrator_login_password']


check = SynapseWorkspaceAdministratorLoginPasswordHidden()
