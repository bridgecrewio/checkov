from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GKEMetadataServerIsEnabled(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="Ensure the GKE Metadata Server is Enabled",
            id="CKV_GCP_69",
            categories=[CheckCategories.KUBERNETES],
            supported_resources=[
                "google_container_cluster",
                "google_container_node_pool",
            ],
        )

    def scan_resource_conf(self, conf):
        # Dedicated Autopilot clusters always use Workload Identity
        # Federation for GKE and the GKE metadata server.
        if conf.get("enable_autopilot") == [True]:
            return CheckResult.PASSED

        # Standard cluster default node pool or standalone node pool.
        for node_config in force_list(conf.get("node_config", [])):
            if not isinstance(node_config, dict):
                continue

            metadata_configs = force_list(
                node_config.get("workload_metadata_config", [])
            )

            for metadata_config in metadata_configs:
                if not isinstance(metadata_config, dict):
                    continue

                # Current Google provider syntax.
                if metadata_config.get("mode") == ["GKE_METADATA"]:
                    return CheckResult.PASSED

                # Older Google provider syntax.
                if (
                    metadata_config.get("node_metadata")
                    == ["GKE_METADATA_SERVER"]
                ):
                    return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self):
        return [
            "enable_autopilot",
            "node_config/[0]/workload_metadata_config/[0]/mode",
            "node_config/[0]/workload_metadata_config/[0]/node_metadata",
        ]


check = GKEMetadataServerIsEnabled()