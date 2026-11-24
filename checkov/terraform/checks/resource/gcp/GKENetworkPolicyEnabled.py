from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GKENetworkPolicyEnabled(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="Ensure Network Policy is enabled on Kubernetes Engine Clusters",
            id="CKV_GCP_12",
            categories=[CheckCategories.KUBERNETES],
            supported_resources=["google_container_cluster"],
        )

    def scan_resource_conf(self, conf):
        # Dedicated Autopilot clusters always use GKE Dataplane V2
        # and enforce Kubernetes NetworkPolicy.
        if conf.get("enable_autopilot") == [True]:
            return CheckResult.PASSED

        # Dataplane V2 enforces Kubernetes NetworkPolicy without
        # requiring the legacy network_policy block.
        if conf.get("datapath_provider") == ["ADVANCED_DATAPATH"]:
            return CheckResult.PASSED

        # Standard cluster using the legacy network-policy configuration.
        for network_policy in force_list(conf.get("network_policy", [])):
            if (
                isinstance(network_policy, dict)
                and network_policy.get("enabled") == [True]
            ):
                return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self):
        return [
            "enable_autopilot",
            "datapath_provider",
            "network_policy/[0]/enabled",
        ]


check = GKENetworkPolicyEnabled()