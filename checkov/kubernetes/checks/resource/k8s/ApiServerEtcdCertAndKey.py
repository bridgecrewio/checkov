from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerEtcdCertAndKey(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_99"
        name = "Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasCertCommand = False
                hasKeyCommand = False
                for command in conf["command"]:
                    if command.startswith("--etcd-certfile"):
                        hasCertCommand = True
                    elif command.startswith("--etcd-keyfile"):
                        hasKeyCommand = True
                return CheckResult.PASSED if hasCertCommand and hasKeyCommand else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerEtcdCertAndKey()
