from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import Any, List


class AllowPrivilegeEscalationPSP(BaseResourceNegativeValueCheck):
    def __init__(self):
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
        supported_resources = ['kubernetes_pod_security_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'spec/[0]/allow_privilege_escalation'

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = AllowPrivilegeEscalationPSP()