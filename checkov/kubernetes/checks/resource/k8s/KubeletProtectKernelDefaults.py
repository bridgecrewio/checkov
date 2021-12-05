from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubeletProtectKernelDefaults(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 4.2.6
        id = "CKV_K8S_144"
        name = "Ensure that the --protect-kernel-defaults argument is set to true"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kubelet" in conf["command"]:
                if "--protect-kernel-defaults=true" not in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = KubeletProtectKernelDefaults()
