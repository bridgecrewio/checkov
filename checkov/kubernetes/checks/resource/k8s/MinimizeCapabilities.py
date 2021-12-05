from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class MinimizeCapabilities(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.5 5.2.9
        name = "Minimize the admission of containers with capabilities assigned"
        id = "CKV_K8S_37"
        # Location: container .securityContext.capabilities.drop
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["securityContext/capabilities/drop"]
        if conf.get("securityContext"):
            if conf["securityContext"].get("capabilities"):
                if conf["securityContext"]["capabilities"].get("drop"):
                    for d in conf["securityContext"]["capabilities"]["drop"]:
                        if any(cap in d for cap in ("ALL", "all")):
                            return CheckResult.PASSED
        return CheckResult.FAILED


check = MinimizeCapabilities()
