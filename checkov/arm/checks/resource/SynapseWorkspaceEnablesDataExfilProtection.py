from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class SynapseWorkspaceEnablesDataExfilProtection(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Synapse workspace has data_exfiltration_protection_enabled"
        id = "CKV_AZURE_157"
        supported_resources = ["Microsoft.Synapse/workspaces"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'properties/dataExfiltrationProtectionEnabled'


check = SynapseWorkspaceEnablesDataExfilProtection()
