from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ACRAdminAccountDisabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ACR admin account is disabled"
        id = "CKV_AZURE_137"
        supported_resources = ['azurerm_container_registry']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # default configuration disables admin account
        if 'admin_enabled' in conf.keys() and conf['admin_enabled'][0] == True:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = ACRAdminAccountDisabled()