from __future__ import annotations

from typing import Any, List

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int


# https://docs.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts

class StorageAccountDefaultNetworkAccessDeny(BaseResourceCheck):
    def __init__(self) -> None:
        # properties.networkAcls.bypass == "AzureServices"
        # Fail if apiVersion less than 2017 as this setting wasn't available
        name = "Ensure default network access rule for Storage Accounts is set to deny"
        id = "CKV_AZURE_35"
        supported_resources = ('Microsoft.Storage/storageAccounts',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "apiVersion" in conf:
            # Fail if apiVersion < 2017 as you could not set networkAcls
            year = force_int(conf["apiVersion"][0:4])

            if year is None:
                return CheckResult.UNKNOWN
            elif year < 2017:
                return CheckResult.FAILED

        if "properties" in conf:
            if "networkAcls" in conf["properties"]:
                if not isinstance(conf["properties"]["networkAcls"], dict):
                    return CheckResult.UNKNOWN
                if "defaultAction" in conf["properties"]["networkAcls"]:
                    if conf["properties"]["networkAcls"]["defaultAction"] == "Deny":
                        return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["apiVersion", "properties", "properties/networkAcls"]


check = StorageAccountDefaultNetworkAccessDeny()
