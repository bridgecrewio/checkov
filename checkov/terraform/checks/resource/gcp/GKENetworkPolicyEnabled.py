from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKENetworkPolicyEnabled(BaseResourceCheck):
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

        # If cluster is type Autopilot short circuit this policy as feature is enabled by default
        if conf.get("enable_autopilot") == [True]:
            return CheckResult.PASSED

        # datapath_provider is a root level resource attribute. Moved from check within network_policy block
        if conf.get('datapath_provider') == ['ADVANCED_DATAPATH']:
            return CheckResult.PASSED

        if 'network_policy' in conf:
            network_policy = conf.get('network_policy')

            if 'enabled' in network_policy[0]:
                policy_enabled = network_policy[0].get('enabled')[0]
                if policy_enabled:
                    return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self):
        return [
                "enable_autopilot",
                "datapath_provider",
                "network_policy/[0]/enabled",
            ]

check = GKENetworkPolicyEnabled()