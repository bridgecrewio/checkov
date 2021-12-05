from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubeletHostnameOverride(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 4.2.8
        id = "CKV_K8S_146"
        name = "Ensure that the --hostname-override argument is not set"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kubelet" in conf["command"]:
                if "--hostname-override" in [arg.split("=")[0] for arg in conf["command"]]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = KubeletHostnameOverride()
