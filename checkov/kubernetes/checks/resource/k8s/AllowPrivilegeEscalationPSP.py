from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class AllowPrivilegeEscalationPSP(BaseK8Check):
    def __init__(self) -> None:
        # CIS-1.3 1.7.5
        # CIS-1.5 5.2.5
        # https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
        # AllowPrivilegeEscalation is true always when the container is: 1) run as Privileged OR 2) has CAP_SYS_ADMIN.
        # https://kubernetes.io/docs/concepts/policy/pod-security-policy/
        # AllowPrivilegeEscalation - This defaults to allow to not break setuid binaries
        # DefaultAllowPrivilegeEscalation - Default is to allow as to not breat setuid binaries
        # If you omit allowPrivilegeEscalation from PSP, it defaults to true
        # Location: PodSecurityPolicy.spec.allowPrivilegeEscalation
        name = "Containers should not run with allowPrivilegeEscalation"
        id = "CKV_K8S_5"
        supported_kind = ('PodSecurityPolicy',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "spec" in conf:
            if "allowPrivilegeEscalation" in conf["spec"]:
                if conf["spec"]["allowPrivilegeEscalation"]:
                    return CheckResult.FAILED
                else:
                    return CheckResult.PASSED
            else:
                return CheckResult.FAILED

        return CheckResult.UNKNOWN


check = AllowPrivilegeEscalationPSP()
