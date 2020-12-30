from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
import re

STO_NAME_REGEX = re.compile('^[a-z0-9]{3,24}$')


class StorageAccountName(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the Storage Account naming rules"
        id = "CKV_AZURE_43"
        supported_resources = ['azurerm_storage_account']
        categories = [CheckCategories.CONVENTION]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            The Storage Account naming reference:
            https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview#naming-storage-accounts
        :param conf: azurerm_storage_account configuration
        :return: <CheckResult>
        """
        return CheckResult.PASSED if conf.get('name') and re.match(STO_NAME_REGEX, conf['name'][0]) else CheckResult.FAILED


check = StorageAccountName()
