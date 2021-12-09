from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck
from checkov.kubernetes.checks.resource.k8s.k8s_check_utils import extract_commands


class EtcdPeerFiles(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6
        id = "CKV_K8S_119"
        name = "Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        keys, values = extract_commands(conf)

        if "etcd" in keys:
            if "--peer-cert-file" not in keys or "--peer-key-file" not in keys:
                return CheckResult.FAILED

        return CheckResult.PASSED


check = EtcdPeerFiles()
