from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerBasicAuthFile(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_69"
        name = "Ensure that the --basic-auth-file argument is not set"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        command = conf.get("command")
        if isinstance(command, list):
            if "kube-apiserver" in command:
                if any(x.startswith("--basic-auth-file") for x in command):
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerBasicAuthFile()
