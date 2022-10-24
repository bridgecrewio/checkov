from typing import Dict, Any

from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class AzureScaleSetPassword(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Azure linux scale set does not use basic authentication(Use SSH Key Instead)"
        id = "CKV_AZURE_49"
        supported_resources = ("Microsoft.Compute/virtualMachineScaleSets",)
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        if isinstance(properties, dict):
            vm_profile = properties.get("virtualMachineProfile")
            if isinstance(vm_profile, dict):
                storage_profile = vm_profile.get("storageProfile")
                if isinstance(storage_profile, dict):
                    image_reference = storage_profile.get("imageReference")
                    if isinstance(image_reference, dict):
                        publisher = image_reference.get("publisher")
                        if publisher and "windows" in publisher.lower():
                            # This check is not relevant to Windows systems
                            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "properties/virtualMachineProfile/osProfile/linuxConfiguration/disablePasswordAuthentication"

    def get_expected_value(self) -> Any:
        return True


check = AzureScaleSetPassword()
