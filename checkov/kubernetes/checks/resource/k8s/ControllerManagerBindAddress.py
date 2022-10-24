from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ControllerManagerBindAddress(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_113"
        name = "Ensure that the --bind-address argument is set to 127.0.0.1"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-controller-manager" in conf["command"]:
                for cmd in conf["command"]:
                    if "=" in cmd:
                        [key, value, *_] = cmd.split("=")
                        if key == "--bind-address" and value == "127.0.0.1":
                            return CheckResult.PASSED
                return CheckResult.FAILED

        return CheckResult.PASSED


check = ControllerManagerBindAddress()
