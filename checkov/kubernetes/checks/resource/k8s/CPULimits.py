from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class CPULimits(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "CPU limits should be set"
        id = "CKV_K8S_11"
        # Location: container .resources.limits.cpu
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["resources/limits/cpu"]
        res = conf.get("resources")
        if res:
            if not isinstance(res, dict):
                return CheckResult.UNKNOWN
            limits = res.get("limits")
            if limits and limits.get("cpu"):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = CPULimits()
