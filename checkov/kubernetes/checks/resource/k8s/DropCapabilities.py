from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class DropCapabilities(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.3 1.7.7
        # CIS-1.5 5.2.7
        # NET_RAW allows a process to spy on packets on its network
        name = "Minimize the admission of containers with the NET_RAW capability"
        id = "CKV_K8S_28"
        # Location: container .securityContext.capabilities.drop
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["securityContext/capabilities/drop"]
        if conf.get("securityContext"):
            if conf["securityContext"].get("capabilities"):
                if conf["securityContext"]["capabilities"].get("drop"):
                    for d in conf["securityContext"]["capabilities"]["drop"]:
                        if any(cap in d for cap in ("ALL", "all", "NET_RAW")):
                            return CheckResult.PASSED
        return CheckResult.FAILED


check = DropCapabilities()
