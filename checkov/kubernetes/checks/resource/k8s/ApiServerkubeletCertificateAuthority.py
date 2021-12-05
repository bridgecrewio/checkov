from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck
from checkov.kubernetes.checks.resource.k8s.k8s_check_utils import extract_commands


class ApiServerkubeletCertificateAuthority(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_73"
        name = "Ensure that the --kubelet-certificate-authority argument is set as appropriate"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        keys, values = extract_commands(conf)

        if "kube-apiserver" in keys and "--kubelet-certificate-authority" not in keys:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerkubeletCertificateAuthority()
