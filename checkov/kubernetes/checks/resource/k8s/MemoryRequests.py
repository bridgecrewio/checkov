from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class MemoryRequests(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "Memory requests should be set"
        id = "CKV_K8S_12"
        # Location: container .resources.requests.memory
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["resources/requests/memory"]
        res = conf.get("resources")
        if res:
            requests = res.get("requests")
            if requests and requests.get("memory"):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = MemoryRequests()
