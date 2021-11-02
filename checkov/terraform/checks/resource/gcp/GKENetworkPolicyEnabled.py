from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKENetworkPolicyEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Network Policy is enabled on Kubernetes Engine Clusters"
        id = "CKV_GCP_12"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for network policy configuration on google_container_cluster:
            https://www.terraform.io/docs/providers/google/r/container_cluster.html
            Expects either network policies or Dataplane V2 to be enabled
        :param conf: google_container_cluster configuration
        :return: <CheckResult>
        """
        if 'network_policy' in conf:
            network_policy = conf.get('network_policy')
            datapath_provider = conf.get('datapath_provider')

            if 'enabled' in network_policy[0]:
                policy_enabled = network_policy[0].get('enabled')
                if policy_enabled:
                    return CheckResult.PASSED
                elif not policy_enabled and datapath_provider == 'ADVANCED_DATAPATH':
                    return CheckResult.PASSED

        return CheckResult.FAILED

    def get_inspected_key(self):
        return 'network_policy/[0]/enabled'


check = GKENetworkPolicyEnabled()
