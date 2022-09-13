from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.kubernetes.checks.resource.base_root_container_check import BaseK8sRootContainerCheck


class RootContainersHighUID(BaseK8sRootContainerCheck):
    def __init__(self) -> None:
        name = "Containers should run as a high UID to avoid host conflict"
        # runAsUser should be >= 10000 at pod spec or container level
        # Location: Pod.spec.runAsUser
        # Location: CronJob.spec.jobTemplate.spec.template.spec.securityContext.runAsUser
        # Location: *.spec.template.spec.securityContext.runAsUser
        id = "CKV_K8S_40"
        super().__init__(name=name, id=id)

    def scan_spec_conf(self, conf: dict[str, Any]) -> CheckResult:
        spec = self.extract_spec(conf)

        # Collect results
        if spec and isinstance(spec, dict):
            results = {"pod": {}, "container": []}
            results["pod"]["runAsUser"] = self.check_runAsUser(spec, 10000)

            containers = spec.get("containers", [])
            if not isinstance(containers, list):
                return CheckResult.UNKNOWN
            for c in containers:
                cresults = {"runAsUser": self.check_runAsUser(c, 10000)}
                results["container"].append(cresults)

            # Evaluate pass / fail - Container values override Pod values
            # Pod runAsUser >= 10000, no override at container (PASSED)
            # Pod runAsUser >= 10000, override at container < 10000 (FAILED)
            # Pod runAsUser < 10000, no override at container (FAILED)
            # Pod runAsUser < 10000, override at container >= 10000 (PASSED)
            # Pod runAsUser not set, container runAsUser not set or < 10000 (FAILED)
            # Pod runAsUser not set, container runAsUser set >= 10000 (PASSED)
            if results["pod"]["runAsUser"] == "PASSED":
                for cr in results["container"]:
                    if cr["runAsUser"] == "FAILED":
                        return CheckResult.FAILED
                return CheckResult.PASSED
            elif results["pod"]["runAsUser"] == "FAILED":
                containeroverride = False
                for cr in results["container"]:
                    if cr["runAsUser"] == "FAILED" or cr["runAsUser"] == "ABSENT":
                        return CheckResult.FAILED
                    elif cr["runAsUser"] == "PASSED":
                        containeroverride = True
                if containeroverride:
                    return CheckResult.PASSED
                return CheckResult.FAILED
            else:
                # Pod runAsUser ABSENT
                containeroverride = False
                for cr in results["container"]:
                    if cr["runAsUser"] == "FAILED" or cr["runAsUser"] == "ABSENT":
                        return CheckResult.FAILED
                    elif cr["runAsUser"] == "PASSED":
                        containeroverride = True
                if containeroverride:
                    return CheckResult.PASSED
                return CheckResult.FAILED

        return CheckResult.FAILED


check = RootContainersHighUID()
