from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int


class StorageAccountsTransportEncryption(BaseResourceCheck):
    def __init__(self):
        # supportsHttpsTrafficOnly: Allows https traffic only to storage service if sets to true. The default value is
        # true since API version 2019-04-01.
        name = "Ensure that 'supportsHttpsTrafficOnly' is set to 'true'"
        id = "CKV_AZURE_3"
        supported_resources = ['Microsoft.Storage/storageAccounts']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "properties" in conf:
            if "supportsHttpsTrafficOnly" in conf["properties"]:
                if str(conf["properties"]["supportsHttpsTrafficOnly"]).lower() == "true":
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED

        # Use default if supportsHttpsTrafficOnly is not set
        if "apiVersion" in conf:
            # Default for apiVersion 2019 and newer is supportsHttpsTrafficOnly = True
            year = force_int(conf["apiVersion"][0:4])

            if year is None:
                return CheckResult.UNKNOWN
            elif year < 2019:
                return CheckResult.FAILED
            else:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = StorageAccountsTransportEncryption()
