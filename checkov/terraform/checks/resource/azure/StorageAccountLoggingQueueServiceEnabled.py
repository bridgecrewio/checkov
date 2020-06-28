from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class StorageAccountLoggingQueueServiceEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Storage logging is enabled for Queue service for read, write and delete requests"
        id = "CKV_AZURE_33"
        supported_resources = ['azurerm_storage_account']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'account_kind' in conf and (conf['account_kind'][0] != 'Storage' or conf['account_kind'][0] != 'StorageV2'):
            # queue_properties block doesn't apply for other account kind
            return CheckResult.PASSED
        if 'queue_properties' in conf and 'logging' in conf['queue_properties'][0]:
            logging = conf['queue_properties'][0]['logging'][0]
            if logging['delete'][0] and logging['write'][0] and logging['read'][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = StorageAccountLoggingQueueServiceEnabled()
