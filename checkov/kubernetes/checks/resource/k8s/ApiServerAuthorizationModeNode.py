from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerAuthorizationModeNode(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_75"
        name = "Ensure that the --authorization-mode argument includes Node"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasNodeAuthorizationMode = False
                for command in conf["command"]:
                    if command.startswith("--authorization-mode"):
                        modes = command.split("=")[1]
                        if "Node" in modes.split(","):
                            hasNodeAuthorizationMode = True
                return CheckResult.PASSED if hasNodeAuthorizationMode else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerAuthorizationModeNode()
