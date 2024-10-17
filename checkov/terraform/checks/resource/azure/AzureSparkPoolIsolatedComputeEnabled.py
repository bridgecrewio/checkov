from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureSparkPoolIsolatedComputeEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure isolated compute is enabled for Synapse Spark pools"
        id = "CKV_AZURE_242"
        supported_resources = ("azurerm_synapse_spark_pool",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "compute_isolation_enabled"


check = AzureSparkPoolIsolatedComputeEnabled()
