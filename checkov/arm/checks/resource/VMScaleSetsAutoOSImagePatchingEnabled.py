from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class VMScaleSetsAutoOSImagePatchingEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that automatic OS image patching is enabled for Virtual Machine Scale Sets"
        id = "CKV_AZURE_95"
        supported_resources = ['Microsoft.Compute/virtualMachineScaleSets']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("properties") and isinstance(conf.get("properties"), dict):
            properties = conf.get("properties")
            self.evaluated_keys = ['properties']

            if properties.get("orchestrationMode") and isinstance(properties.get("orchestrationMode"), str):
                if properties.get("orchestrationMode") == "Flexible":
                    self.evaluated_keys = ['properties/orchestrationMode']
                    return CheckResult.FAILED

            if properties.get("virtualMachineProfile") and isinstance(properties.get("virtualMachineProfile"), dict):
                virtualMachineProfile = properties.get("virtualMachineProfile")
                self.evaluated_keys = ['properties/virtualMachineProfile']

                if virtualMachineProfile.get("extensionProfile") and isinstance(virtualMachineProfile.get("extensionProfile"), dict):
                    extensionProfile = virtualMachineProfile.get("extensionProfile")
                    self.evaluated_keys = ['properties/virtualMachineProfile/extensionProfile']

                    if extensionProfile.get("extensions") and isinstance(extensionProfile.get("extensions"), list):
                        extensions = extensionProfile.get("extensions")
                        self.evaluated_keys = ['properties/virtualMachineProfile/extensionProfile/extensions']

                        for extension in extensions:
                            if extension.get("properties") and isinstance(extension.get("properties"), dict):
                                properties = extension.get("properties")
                                if properties.get("enableAutomaticUpgrade") is True and isinstance(properties.get("autoUpgradeMinorVersion"), bool):
                                    return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = VMScaleSetsAutoOSImagePatchingEnabled()
