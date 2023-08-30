from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck
from typing import Any


class MySQLEncryptionEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that MySQL server enables infrastructure encryption"
        id = "CKV_AZURE_96"
        supported_resources = ['Microsoft.DBforMySQL/flexibleServers']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if conf.get("properties") and isinstance(conf.get("properties"), dict):
            properties = conf.get("properties")
            self.evaluated_keys = ['properties']

            if properties.get('dataencryption') and isinstance(properties.get('dataencryption'), dict):
                dataencryption = properties.get('dataencryption')
                self.evaluated_keys = ['properties/dataencryption']
                if dataencryption is None:
                    return CheckResult.FAILED

                return CheckResult.PASSED
            # unparsed
            if properties.get('dataencryption') and isinstance(properties.get('dataencryption'), str):
                return CheckResult.UNKNOWN
            return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = MySQLEncryptionEnabled()
