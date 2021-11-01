from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEMetadataServerisEnabled(BaseResourceValueCheck):
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
            if 'workload_metadata_config' in conf['node_config'][0].keys():
                workload_metadata_config = conf['node_config'][0]["workload_metadata_config"]
                
                # deprecated in newer google provider
                if 'node_metadata' in workload_metadata_config[0].keys():
                    node_metadata = workload_metadata_config[0]["node_metadata"]
                    return CheckResult.PASSED if node_metadata == "GKE_METADATA_SERVER" else CheckResult.FAILED

                if 'mode' in workload_metadata_config[0].keys():
                    mode = workload_metadata_config[0]["mode"]
                    return CheckResult.PASSED if mode == "GKE_METADATA" else CheckResult.FAILED

                return CheckResult.FAILED
            return CheckResult.FAILED
        return CheckResult.FAILED

    def get_inspected_key(self):
        return 'node_config/[0]/workload_metadata_config'

check = GKEMetadataServerisEnabled()
