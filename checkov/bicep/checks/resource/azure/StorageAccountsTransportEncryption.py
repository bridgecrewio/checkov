from __future__ import annotations

from typing import Any

from checkov.bicep.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int


class StorageAccountsTransportEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that 'supportsHttpsTrafficOnly' is set to 'true'"
        id = "CKV_AZURE_3"
        supported_resources = ("Microsoft.Storage/storageAccounts",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["properties/supportsHttpsTrafficOnly"]
        properties = conf.get("properties")
        if properties:
            https_only = properties.get("supportsHttpsTrafficOnly")
            if https_only is True:
                return CheckResult.PASSED
            elif https_only is False:
                return CheckResult.FAILED

        year = force_int(self.api_version[:4])
        if year is None:
            return CheckResult.UNKNOWN
        elif year < 2019:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = StorageAccountsTransportEncryption()
