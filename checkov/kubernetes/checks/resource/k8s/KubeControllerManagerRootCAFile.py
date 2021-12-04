from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubeControllerManagerRootCAFile(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_111"
        name = "Ensure that the --root-ca-file argument is set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-controller-manager" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith("--root-ca-file"):
                        file_name = command.split("=")[1]
                        extension = file_name.split(".")[1]
                        if extension == "pem":
                            return CheckResult.PASSED
                        else:
                            return CheckResult.FAILED
        return CheckResult.PASSED


check = KubeControllerManagerRootCAFile()
