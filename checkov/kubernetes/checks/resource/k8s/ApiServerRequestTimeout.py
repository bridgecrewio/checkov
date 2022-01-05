import re
from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerRequestTimeout(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_95"
        name = "Ensure that the --request-timeout argument is set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if "command" in conf:
            if "kube-apiserver" in conf["command"]:
                for cmd in conf["command"]:
                    if cmd == "--request-timeout":
                        return CheckResult.FAILED
                    if "=" in cmd:
                        [field, value, *_] = cmd.split("=")
                        if field == "--request-timeout":
                            regex = re.compile(
                                r"^(\d{1,2}[h])(\d{1,2}[m])?(\d{1,2}[s])?$|^(\d{1,2}[m])?(\d{1,2}[s])?$|^(\d{1,2}[s])$"
                            )
                            matches = re.match(regex, value)
                            if not matches:
                                return CheckResult.FAILED
        return CheckResult.PASSED


check = ApiServerRequestTimeout()
