from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class AllowedCapabilities(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.5 5.2.8
        name = "Minimize the admission of containers with added capability"
        # Do not generally permit containers with capabilities assigned beyond the default set
        # https://kubernetes.io/docs/concepts/policy/pod-security-policy/#capabilities
        # Location: container .securityContext.capabilities
        id = "CKV_K8S_25"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["securityContext/capabilities/add"]
        if conf.get("securityContext"):
            if conf["securityContext"].get("capabilities"):
                if conf["securityContext"]["capabilities"].get("add"):
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = AllowedCapabilities()
