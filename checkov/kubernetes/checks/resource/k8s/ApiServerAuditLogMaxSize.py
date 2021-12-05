from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerAuditLogMaxSize(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_94"
        name = "Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasAuditLogMaxSize = False
                for command in conf["command"]:
                    if command.startswith("--audit-log-maxsize"):
                        value = command.split("=")[1]
                        hasAuditLogMaxSize = int(value) >= 100
                        break
                return CheckResult.PASSED if hasAuditLogMaxSize else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerAuditLogMaxSize()
