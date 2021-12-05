from typing import Dict, Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ReadOnlyFilesystem(BaseK8sContainerCheck):
    def __init__(self) -> None:
        name = "Use read-only filesystem for containers where possible"
        id = "CKV_K8S_22"
        # Location: container .securityContext.readOnlyRootFilesystem
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["securityContext/readOnlyRootFilesystem"]
        if conf.get("securityContext"):
            if conf["securityContext"].get("readOnlyRootFilesystem"):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = ReadOnlyFilesystem()
