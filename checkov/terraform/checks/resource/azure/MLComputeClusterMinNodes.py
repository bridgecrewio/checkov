from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MLComputeClusterMinNodes(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Machine Learning Compute Cluster Minimum Nodes Set To 0"
        id = "CKV_AZURE_150"
        supported_resources = ['azurerm_machine_learning_compute_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "scale_settings/[0]/min_node_count"

    def get_expected_value(self):
        return 0


check = MLComputeClusterMinNodes()
