from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.util.data_structures_utils import find_in_dict


class AzureManagedDiscEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Azure managed disk have encryption enabled"
        id = "CKV_AZURE_2"
        supported_resources = ("Microsoft.Compute/disks",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        if properties:
            encryption = properties.get("encryption")
            if encryption:
                # if the block exists, then it is enabled
                return CheckResult.PASSED

            encryption_enabled = find_in_dict(input_dict=properties, key_path="encryptionSettingsCollection/enabled")
            if str(encryption_enabled).lower() == "true":
                return CheckResult.PASSED

            encryption_enabled = find_in_dict(input_dict=properties, key_path="encryptionSettings/enabled")
            if str(encryption_enabled).lower() == "true":
                return CheckResult.PASSED

        return CheckResult.FAILED


check = AzureManagedDiscEncryption()
