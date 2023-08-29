from typing import Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class VMDisablePasswordAuthentication(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Virtual machine does not enable password authentication"
        id = "CKV_AZURE_149"
        supported_resources = ['Microsoft.Compute/virtualMachineScaleSets', 'Microsoft.Compute/virtualMachines']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:

        if conf.get('properties') and isinstance(conf.get('properties'), dict):
            properties = conf.get('properties')
            if properties.get("virtualMachineProfile") and isinstance(properties.get("virtualMachineProfile"), dict):
                profile = properties.get("virtualMachineProfile")
                if profile.get("osProfile") and isinstance(profile.get("osProfile"), dict):
                    osProfile = profile.get("osProfile")
            if properties.get("osProfile") and isinstance(properties.get("osProfile"), dict):
                osProfile = properties.get("osProfile")
            if osProfile is None:
                return CheckResult.UNKNOWN
            if osProfile.get("linuxConfiguration") and isinstance(osProfile.get("linuxConfiguration"), dict):
                config = osProfile.get("linuxConfiguration")
                if config.get("disablePasswordAuthentication") and isinstance(config.get("disablePasswordAuthentication"), bool):
                    return CheckResult.PASSED
                return CheckResult.FAILED
            return CheckResult.UNKNOWN

        return CheckResult.FAILED


check = VMDisablePasswordAuthentication()
