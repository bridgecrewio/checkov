from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerTlsCertAndKey(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_100"
        name = "Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-apiserver" in conf["command"]:
                hasCertCommand = False
                hasKeyCommand = False
                for command in conf["command"]:
                    if command.startswith("--tls-cert-file"):
                        if len(command.split("=")) == 2 and (command.split("=")[1]).strip():
                            hasCertCommand = True
                    elif command.startswith("--tls-private-key-file"):
                        if len(command.split("=")) == 2 and (command.split("=")[1]).strip():
                            hasKeyCommand = True
                return CheckResult.PASSED if hasCertCommand and hasKeyCommand else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerTlsCertAndKey()
