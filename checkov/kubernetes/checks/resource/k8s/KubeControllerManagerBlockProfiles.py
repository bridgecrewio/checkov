from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubeControllerManagerBlockProfiles(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_107"
        name = "Ensure that the --profiling argument is set to false"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-controller-manager" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith("--profiling"):
                        value = command.split("=")[1]
                        if value == "false":
                            return CheckResult.PASSED
                return CheckResult.FAILED
        return CheckResult.PASSED


check = KubeControllerManagerBlockProfiles()
