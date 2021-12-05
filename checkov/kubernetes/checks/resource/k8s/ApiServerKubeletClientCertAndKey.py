from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerKubeletClientCertAndKey(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_72"
        name = "Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-apiserver" in conf["command"]:
                hasCertCommand = False
                hasKeyCommand = False
                for command in conf["command"]:
                    if command.startswith("--kubelet-client-certificate"):
                        hasCertCommand = True
                    elif command.startswith("--kubelet-client-key"):
                        hasKeyCommand = True
                return CheckResult.PASSED if hasCertCommand and hasKeyCommand else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerKubeletClientCertAndKey()
