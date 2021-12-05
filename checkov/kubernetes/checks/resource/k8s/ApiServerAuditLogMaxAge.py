from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerAuditLogMaxAge(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_92"
        name = "Ensure that the --audit-log-maxage argument is set to 30 or as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasAuditLogMaxAge = False
                for command in conf["command"]:
                    if command.startswith("--audit-log-maxage"):
                        value = command.split("=")[1]
                        hasAuditLogMaxAge = int(value) >= 30
                        break
                return CheckResult.PASSED if hasAuditLogMaxAge else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerAuditLogMaxAge()
