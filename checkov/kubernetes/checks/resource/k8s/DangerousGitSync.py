from typing import Any, Dict

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class DangerousGitSync(BaseK8sContainerCheck):
    def __init__(self) -> None:
        # Use of GITSYNC_GIT has potential for code injection
        # https://www.akamai.com/blog/security-research/2024-august-kubernetes-gitsync-command-injection-defcon
        name = "Limit the use of git-sync to prevent code injection"
        id = "CKV_K8S_159"
        # Location: spec.template.spec.containers[*].env[*].name
        # Location2: spec.template.spec.initContainers[*].env[*].name
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["env"]
        if conf.get("env") and isinstance(conf.get("env"), list):
            for env in conf.get("env", []):
                if env.get("name") and env.get("name") == "GITSYNC_GIT":
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = DangerousGitSync()
