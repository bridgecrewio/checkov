from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AzureInstanceExtensions(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Virtual Machine Extensions are not Installed"
        id = "CKV_AZURE_50"
        supported_resources = ["Microsoft.Compute/virtualMachines"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/osProfile/allowExtensionOperations"

    def get_expected_value(self) -> bool:
        return False


check = AzureInstanceExtensions()
