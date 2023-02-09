from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class CPURequests(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "CPU requests should be set"
        id = "CKV_K8S_10"
        # Location: container .resources.requests.cpu
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["resources/requests/cpu"]
        res = conf.get("resources")
        if res:
            if not isinstance(res, dict):
                return CheckResult.UNKNOWN
            requests = res.get("requests")
            if not isinstance(requests, dict):
                return CheckResult.UNKNOWN
            if requests and requests.get("cpu"):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = CPURequests()
