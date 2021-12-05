from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class EtcdClientCertAuth(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 2.2
        id = "CKV_K8S_117"
        name = "Ensure that the --client-cert-auth argument is set to true"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if "etcd" in conf.get("command", []) and "--client-cert-auth=true" not in conf.get("command", []):
            return CheckResult.FAILED

        return CheckResult.PASSED


check = EtcdClientCertAuth()
