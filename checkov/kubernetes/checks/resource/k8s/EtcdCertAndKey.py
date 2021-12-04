from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class EtcdCertAndKey(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 2.1
        id = "CKV_K8S_116"
        name = "Ensure that the --cert-file and --key-file arguments are set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "etcd" in conf["command"]:
                hasCertCommand = False
                hasKeyCommand = False
                for command in conf["command"]:
                    if command.startswith("--cert-file"):
                        hasCertCommand = True
                    elif command.startswith("--key-file"):
                        hasKeyCommand = True
                    if hasCertCommand and hasKeyCommand:
                        return CheckResult.PASSED
                return CheckResult.FAILED

        return CheckResult.PASSED


check = EtcdCertAndKey()
