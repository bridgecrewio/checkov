from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEMasterAuthorizedNetworksEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure master authorized networks is set to enabled in GKE clusters"
        id = "CKV_GCP_20"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/google/r/compute_ssl_policy.html
        :param conf: google_compute_ssl_policy configuration
        :return: <CheckResult>
        """
        if 'master_authorized_networks_config' in conf.keys():
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GKEMasterAuthorizedNetworksEnabled()
