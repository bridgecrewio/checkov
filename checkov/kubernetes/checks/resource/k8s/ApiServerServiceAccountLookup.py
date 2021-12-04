from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerServiceAccountLookup(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_96"
        name = "Ensure that the --service-account-lookup argument is set to true"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                if (
                    "--service-account-lookup=false" in conf["command"]
                    or "--service-account-lookup=true" not in conf["command"]
                ):
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerServiceAccountLookup()
