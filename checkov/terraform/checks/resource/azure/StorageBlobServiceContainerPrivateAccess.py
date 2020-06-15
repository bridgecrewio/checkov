from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class StorageBlobServiceContainerPrivateAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'Public access level' is set to Private for blob containers"
        id = "CKV_AZURE_34"
        supported_resources = ['azurerm_storage_container']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'container_access_type' in conf and conf['container_access_type'][0] != 'private':
            return CheckResult.FAILED
        return CheckResult.PASSED


check = StorageBlobServiceContainerPrivateAccess()
