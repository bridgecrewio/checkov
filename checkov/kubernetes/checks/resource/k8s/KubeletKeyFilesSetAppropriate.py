from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubeletKeyFilesSetAppropriate(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 4.2.10
        id = "CKV_K8S_148"
        name = "Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kubelet" in conf["command"]:
                hasTLSCert = False
                hasTLSKey = False
                for command in conf["command"]:
                    if command.startswith("--tls-cert-file"):
                        hasTLSCert = True
                    elif command.startswith("--tls-private-key-file"):
                        hasTLSKey = True
                return CheckResult.PASSED if hasTLSCert and hasTLSKey else CheckResult.FAILED

        return CheckResult.PASSED


check = KubeletKeyFilesSetAppropriate()
