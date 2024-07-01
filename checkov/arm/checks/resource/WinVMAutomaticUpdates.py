from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class WinVMAutomaticUpdates(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Windows VM enables automatic updates"
        id = "CKV_AZURE_177"
        supported_resources = ("Microsoft.Compute/virtualMachines", "Microsoft.Compute/virtualMachineScaleSets")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED,)

    def get_inspected_key(self) -> str:
        if self.entity_type == "Microsoft.Compute/virtualMachineScaleSets":
            return "properties/virtualMachineProfile/osProfile/windowsConfiguration/enableAutomaticUpdates"
        return "properties/osProfile/windowsConfiguration/enableAutomaticUpdates"


check = WinVMAutomaticUpdates()
