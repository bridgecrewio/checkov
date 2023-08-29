from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class VMScaleSetsAutoOSImagePatchingEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that automatic OS image patching is enabled for Virtual Machine Scale Sets"
        id = "CKV_AZURE_95"
        supported_resources = ['Microsoft.Compute/virtualMachineScaleSets']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_expected_value(self) -> bool:
        return True

    def get_inspected_key(self) -> str:
        return "properties/virtualMachineProfile/extensionProfile/extensions/[0]/properties/enableAutomaticUpgrade"


check = VMScaleSetsAutoOSImagePatchingEnabled()
