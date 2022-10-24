from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubletEventCapture(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 4.2.9
        id = "CKV_K8S_147"
        name = "Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kubelet" in conf["command"]:
                for cmd in conf["command"]:
                    if "=" in cmd:
                        [key, value, *_] = cmd.split("=")
                        if key == "--event-qps":
                            if int(value) > 5:
                                return CheckResult.FAILED

        return CheckResult.PASSED


check = KubletEventCapture()
