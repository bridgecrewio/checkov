from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class AllowPrivilegeEscalation(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.3 1.7.5
        # CIS-1.5 5.2.5
        # https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
        # https://kubernetes.io/docs/concepts/policy/pod-security-policy/
        # Default is allow / true
        # AllowPrivilegeEscalation is true always when the container is: 1) run as Privileged OR 2) has CAP_SYS_ADMIN.
        # This could be enforced via PodSecurityPolicy
        name = "Containers should not run with allowPrivilegeEscalation"
        id = "CKV_K8S_20"
        # Location: container .securityContext.allowPrivilegeEscalation
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["securityContext/allowPrivilegeEscalation"]
        if conf.get("securityContext"):
            if conf["securityContext"].get("allowPrivilegeEscalation") is False:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = AllowPrivilegeEscalation()
