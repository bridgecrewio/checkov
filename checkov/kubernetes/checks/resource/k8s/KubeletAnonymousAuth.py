from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class KubeletAnonymousAuth(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # CIS-1.6 4.2.1
        id = "CKV_K8S_138"
        name = "Ensure that the --anonymous-auth argument is set to false"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kubelet" in conf["command"]:
                if "--anonymous-auth=true" in conf["command"] or "--anonymous-auth=false" not in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = KubeletAnonymousAuth()
