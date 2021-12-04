from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubeControllerManagerRotateKubeletServerCertificate(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 4.2.12
        id = "CKV_K8S_112"
        name = "Ensure that the RotateKubeletServerCertificate argument is set to true"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-controller-manager" in conf["command"]:
                for cmd in conf["command"]:
                    if cmd.startswith("--feature-gates"):
                        value = cmd[cmd.index("=") + 1 :]
                        if "RotateKubeletServerCertificate=false" in value:
                            return CheckResult.FAILED

        return CheckResult.PASSED


check = KubeControllerManagerRotateKubeletServerCertificate()
