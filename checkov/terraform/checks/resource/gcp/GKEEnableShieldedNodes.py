from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories

class GKEEnableShieldedNodes(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Shielded GKE Nodes are Enabled"
        id = "CKV_GCP_71"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'enable_shielded_nodes'

    def get_expected_value(self):
        return True

check = GKEEnableShieldedNodes()
