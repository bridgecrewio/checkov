from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class SynapseWorkspaceVAisEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Synapse Workspace vulnerability assessment is enabled"
        id = "CKV2_AZURE_46"
        supported_resources = ["Microsoft.Synapse/workspaces/vulnerabilityAssessments"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'properties/recurringScans/isEnabled'


check = SynapseWorkspaceVAisEnabled()
