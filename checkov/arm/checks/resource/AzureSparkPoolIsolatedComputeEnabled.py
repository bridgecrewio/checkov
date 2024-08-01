from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AzureSparkPoolIsolatedComputeEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure isolated compute is enabled for Synapse Spark pools"
        id = "CKV_AZURE_242"
        supported_resources = ["Microsoft.Synapse/workspaces/bigDataPools"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'properties/isComputeIsolationEnabled'


check = AzureSparkPoolIsolatedComputeEnabled()
