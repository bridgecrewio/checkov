from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck
from checkov.kubernetes.checks.resource.k8s.Tiller import Tiller


class TillerDeploymentListener(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "Ensure the Tiller Deployment (Helm V2) is not accessible from within the cluster"
        id = "CKV_K8S_45"
        # Location: container .image
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["image"]
        if not Tiller.is_tiller(metadata, conf):
            return CheckResult.UNKNOWN

        self.evaluated_container_keys.append("arge")
        args = conf.get("args")
        if args:
            for arg in args:
                if "--listen" in arg and ("localhost" in arg or "127.0.0.1" in arg):
                    return CheckResult.PASSED

        return CheckResult.FAILED


check = TillerDeploymentListener()
