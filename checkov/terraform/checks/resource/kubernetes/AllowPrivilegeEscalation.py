from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import Any, List


class AllowPrivilegeEscalation(BaseResourceCheck):

    def __init__(self):
        # CIS-1.3 1.7.5
        # CIS-1.5 5.2.5
        # https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
        # AllowPrivilegeEscalation is true always when the container is: 1) run as Privileged OR 2) has CAP_SYS_ADMIN.
        # https://kubernetes.io/docs/concepts/policy/pod-security-policy/
        # AllowPrivilegeEscalation - This defaults to allow to not break setuid binaries
        # DefaultAllowPrivilegeEscalation - Default is to allow as to not break setuid binaries

        name = "Containers should not run with allowPrivilegeEscalation"
        id = "CKV_K8S_20"
        supported_resources = ['kubernetes_pod']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf.get('spec')[0]
        if spec:
            containers = spec.get("container")
            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN
                if container.get("security_context"):
                    context = container.get("security_context")[0]
                    if context.get("allow_privilege_escalation"):
                        if context.get("allow_privilege_escalation") == [True]:
                            self.evaluated_keys = [f'spec/[0]/container/[{idx}]/security_context/[0]/'
                                                   f'allow_privilege_escalation']
                            return CheckResult.FAILED
            return CheckResult.PASSED


check = AllowPrivilegeEscalation()
