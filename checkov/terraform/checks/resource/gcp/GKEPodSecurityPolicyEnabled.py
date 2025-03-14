from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class GKEPodSecurityPolicyEnabled(BaseResourceCheck):

    """
     Pod Security Policy was removed from GKE clusters with version >= 1.25.0
    """

    def __init__(self):
        name = "Ensure PodSecurityPolicy controller is enabled on the Kubernetes Engine Clusters"
        id = "CKV_GCP_24"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:

        if conf.get('min_master_version') and isinstance(conf.get('min_master_version'), list):
            raw = conf.get('min_master_version')[0]
            splitter = raw.split(".")
            if len(splitter) >= 2:
                str_version = splitter[0] + "." + splitter[1]
                try:
                    version = float(str_version)
                except (ValueError, IndexError):
                    return CheckResult.UNKNOWN
                if version < 1.25:
                    if conf.get('pod_security_policy_config') and isinstance(conf.get('pod_security_policy_config'), list):
                        policy = conf.get('pod_security_policy_config')[0]
                        if policy.get('enabled') and isinstance(policy.get('enabled'), list):
                            secure = policy.get('enabled')[0]
                            if secure:
                                return CheckResult.PASSED
                    self.evaluated_keys = ['min_master_version', 'pod_security_policy_config/[0]/enabled']
                    return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = GKEPodSecurityPolicyEnabled()
