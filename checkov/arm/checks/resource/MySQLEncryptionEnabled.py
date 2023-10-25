from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class MySQLEncryptionEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that MySQL server enables infrastructure encryption"
        id = "CKV_AZURE_96"
        supported_resources = ("Microsoft.DBforMySQL/flexibleServers",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        if properties and isinstance(properties, dict):
            self.evaluated_keys = ["properties/dataencryption"]
            data_encryption = properties.get("dataencryption")
            if data_encryption and isinstance(data_encryption, dict):
                if data_encryption is None:
                    return CheckResult.FAILED
                return CheckResult.PASSED
            # unparsed
            elif data_encryption and isinstance(data_encryption, str):
                return CheckResult.UNKNOWN
            return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = MySQLEncryptionEnabled()
