from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerKubeletHttps(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_71"
        name = "Ensure that the --kubelet-https argument is set to true"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-apiserver" in conf["command"]:
                if "--kubelet-https=false" in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerKubeletHttps()
