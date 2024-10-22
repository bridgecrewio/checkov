from __future__ import annotations

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck

from typing import Any

from checkov.common.util.data_structures_utils import find_in_dict


class VMEncryptionAtHostEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Virtual machine scale sets have encryption at host enabled"
        id = "CKV_AZURE_97"
        supported_resources = ("Microsoft.Compute/virtualMachineScaleSets", "Microsoft.Compute/virtualMachines")
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        encryption = ""

        if self.entity_type == "Microsoft.Compute/virtualMachines":
            self.evaluated_keys = ["properties/securityProfile/encryptionAtHost"]
            encryption = find_in_dict(input_dict=conf, key_path="properties/securityProfile/encryptionAtHost")
        elif self.entity_type == "Microsoft.Compute/virtualMachineScaleSets":
            self.evaluated_keys = ["properties/virtualMachineProfile/securityProfile/encryptionAtHost"]
            encryption = find_in_dict(
                input_dict=conf, key_path="properties/virtualMachineProfile/securityProfile/encryptionAtHost"
            )

        if str(encryption).lower() == "true":
            return CheckResult.PASSED

        return CheckResult.FAILED


check = VMEncryptionAtHostEnabled()
