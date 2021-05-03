from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GKEMetadataServerisEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the GKE Metadata Server is Enabled"
        id = "CKV_GCP_69"
        supported_resources = ['google_container_cluster','google_container_node_pool']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'node_config/[0]/workload_metadata_config/[0]/node_metadata'

    def get_expected_value(self):
        return "GKE_METADATA_SERVER"


check = GKEMetadataServerisEnabled()
