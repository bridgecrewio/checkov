from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck
from checkov.kubernetes.checks.resource.k8s.k8s_check_utils import extract_commands


class ApiServerEtcdCaFile(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_102"
        name = "Ensure that the --etcd-ca-file argument is set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        keys, values = extract_commands(conf)

        if "kube-apiserver" in keys:
            if "--etcd-ca-file" not in keys:
                return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerEtcdCaFile()
