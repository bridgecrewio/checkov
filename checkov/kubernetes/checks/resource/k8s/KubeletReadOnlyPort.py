from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck
from checkov.kubernetes.checks.resource.k8s.k8s_check_utils import extract_commands


class KubeletReadOnlyPort(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 4.2.4
        id = "CKV_K8S_141"
        name = "Ensure that the --read-only-port argument is set to 0"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        keys, values = extract_commands(conf)

        if "kubelet" in keys:
            if "--read-only-port" in keys and values[keys.index("--read-only-port")] == "0":
                return CheckResult.PASSED
            return CheckResult.FAILED

        return CheckResult.PASSED


check = KubeletReadOnlyPort()
