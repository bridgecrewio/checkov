from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubeControllerManagerServiceAccountCredentials(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_108"
        name = "Ensure that the --use-service-account-credentials argument is set to true"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-controller-manager" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith("--use-service-account-credentials"):
                        value = command.split("=")[1]
                        if value == "true":
                            return CheckResult.PASSED
                return CheckResult.FAILED
        return CheckResult.PASSED


check = KubeControllerManagerServiceAccountCredentials()
