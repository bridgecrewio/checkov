from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.util.data_structures_utils import find_in_dict


class VMScaleSetsAutoOSImagePatchingEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that automatic OS image patching is enabled for Virtual Machine Scale Sets"
        id = "CKV_AZURE_95"
        supported_resources = ("Microsoft.Compute/virtualMachineScaleSets",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        if properties and isinstance(properties, dict):
            if properties.get("orchestrationMode") == "Flexible":
                self.evaluated_keys = ["properties/orchestrationMode"]
                return CheckResult.FAILED

            self.evaluated_keys = ["properties/virtualMachineProfile/extensionProfile/extensions"]
            extensions = find_in_dict(
                input_dict=properties,
                key_path="virtualMachineProfile/extensionProfile/extensions",
            )
            if extensions:
                for extension in extensions:
                    extension_properties = extension.get("properties")
                    if extension_properties and isinstance(extension_properties, dict):
                        if extension_properties.get("enableAutomaticUpgrade") is True:
                            return CheckResult.PASSED

            return CheckResult.FAILED

        return CheckResult.UNKNOWN


check = VMScaleSetsAutoOSImagePatchingEnabled()
