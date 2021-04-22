from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts
# https://docs.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts/queueservices

# https://github.com/MicrosoftDocs/azure-docs/issues/13195

# This check is only relevant for storageAccounts with Queue Service enabled

class StorageAccountLoggingQueueServiceEnabled(BaseResourceCheck):
    def __init__(self):
        # properties.networkAcls.bypass == "AzureServices"
        # Fail if apiVersion less than 2017 as this setting wasn't available
        name = "Ensure Storage logging is enabled for Queue service for read, write and delete requests"
        id = "CKV_AZURE_33"
        supported_resources = ['Microsoft.Storage/storageAccounts/queueServices/providers/diagnosticsettings']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "properties" in conf:
            if "logs" in conf["properties"]:
                if conf["properties"]["logs"]:
                    storage = {}
                    for log in conf["properties"]["logs"]:
                        if "category" in log and "enabled" in log:
                            if str(log["enabled"]).lower() == "true":
                                storage[log["category"]] = True
                    if "StorageRead" in storage.keys() and \
                            "StorageWrite" in storage.keys() and \
                            "StorageDelete" in storage.keys():
                        if storage["StorageRead"] and storage["StorageWrite"] and storage["StorageDelete"]:
                            return CheckResult.PASSED
        return CheckResult.FAILED

check = StorageAccountLoggingQueueServiceEnabled()