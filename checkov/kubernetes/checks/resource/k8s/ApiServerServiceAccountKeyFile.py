import re
from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerServiceAccountKeyFile(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_97"
        name = "Ensure that the --service-account-key-file argument is set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-apiserver" in conf["command"]:
                for cmd in conf["command"]:
                    if cmd == "--service-account-key-file":
                        return CheckResult.FAILED
                    if "=" in cmd:
                        [field, value, *_] = cmd.split("=")
                        if field == "--service-account-key-file":
                            # should be a valid path and to end with .pem
                            regex = re.compile(r"^(.*)\.pem$")
                            matches = re.match(regex, value)
                            if not matches:
                                return CheckResult.FAILED
        return CheckResult.PASSED


check = ApiServerServiceAccountKeyFile()
