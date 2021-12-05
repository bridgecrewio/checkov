from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerNodeRestrictionPlugin(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_85"
        name = "Ensure that the admission control plugin NodeRestriction is set"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-apiserver" in conf["command"]:
                for cmd in conf["command"]:
                    if cmd == "--enable-admission-plugins":
                        return CheckResult.FAILED
                    if "=" in cmd:
                        [field, value, *_] = cmd.split("=")
                        if field == "--enable-admission-plugins":
                            if "NodeRestriction" not in value:
                                return CheckResult.FAILED
        return CheckResult.PASSED


check = ApiServerNodeRestrictionPlugin()
