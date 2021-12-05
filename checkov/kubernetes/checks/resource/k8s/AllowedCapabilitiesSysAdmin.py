from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class AllowedCapabilitiesSysAdmin(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "Do not use the CAP_SYS_ADMIN linux capability"
        # This provides the most privilege and is similar to root
        # https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
        id = "CKV_K8S_39"
        # Location: container .securityContext.capabilities
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["securityContext/capabilities/add"]
        if conf.get("securityContext"):
            if conf["securityContext"].get("capabilities"):
                if conf["securityContext"]["capabilities"].get("add"):
                    if "SYS_ADMIN" in conf["securityContext"]["capabilities"]["add"]:
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = AllowedCapabilitiesSysAdmin()
