from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerAuditLog(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_91"
        name = "Ensure that the --audit-log-path argument is set"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasAuditLog = False
                for command in conf["command"]:
                    if command.startswith("--audit-log-path"):
                        hasAuditLog = True
                return CheckResult.PASSED if hasAuditLog else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerAuditLog()
