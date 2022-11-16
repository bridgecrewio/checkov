from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class MemoryLimits(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "Memory limits should be set"
        id = "CKV_K8S_13"
        # Location: container .resources.limits.memory
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["resources/limits/memory"]
        res = conf.get("resources")
        if res:
            if not isinstance(res, dict):
                return CheckResult.UNKNOWN
            limits = res.get("limits")
            if limits and limits.get("memory"):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = MemoryLimits()
