from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class GoogleContainerClusterNetworkPolicyEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Network Policy is enabled on Kubernetes Engine Clusters"
        id = "CKV_GCP_12"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for monitoring configuration on google_container_cluster:
            https://www.terraform.io/docs/providers/google/r/container_cluster.html
        :param conf: google_container_cluster configuration
        :return: <CheckResult>
        """
        if 'network_policy' in conf:
            if 'enabled' in conf['network_policy'][0]:
                if conf['network_policy'][0]['enabled']:
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = GoogleContainerClusterNetworkPolicyEnabled()
