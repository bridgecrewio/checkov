from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEMetadataServerisEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the GKE Metadata Server is Enabled"
        id = "CKV_GCP_69"
        supported_resources = ['google_container_cluster','google_container_node_pool']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


    def scan_resource_conf(self, conf):
        """
        looks for workload_metadata_config in node_config which ensures that the metadata server is enabled
        https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_cluster
        :param conf: google_container_cluster or google_container_node_pool configuration
        :return: <CheckResult>
        """
        if 'node_config' in conf.keys():
            node = conf["node_config"][0]
            if isinstance(node, dict) and 'workload_metadata_config' in node:
                workload_metadata = node["workload_metadata_config"][0]
              
                if workload_metadata.get("mode", None) == ["GKE_METADATA"]:
                    return CheckResult.PASSED
                # deprecated in newer Google provider
                elif workload_metadata.get("node_metadata", None) == ["GKE_METADATA_SERVER"]:
                    return CheckResult.PASSED
            
            return CheckResult.FAILED
        return CheckResult.FAILED

check = GKEMetadataServerisEnabled()
