from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubeControllerManagerServiceAccountPrivateKeyFile(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_110"
        name = "Ensure that the --service-account-private-key-file argument is set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-controller-manager" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith("--service-account-private-key-file"):
                        file_name = command.split("=")[1]
                        extension = file_name.split(".")[1]
                        if extension == "pem":
                            return CheckResult.PASSED
                        else:
                            return CheckResult.FAILED
        return CheckResult.PASSED


check = KubeControllerManagerServiceAccountPrivateKeyFile()
