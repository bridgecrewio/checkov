from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class AllowPrivilegeEscalation(BaseK8Check):

    def __init__(self):
        # CIS-1.3 1.7.5
        # CIS-1.5 5.2.5
        # https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
        #https://kubernetes.io/docs/concepts/policy/pod-security-policy/
        # Default is allow / true
        # AllowPrivilegeEscalation is true always when the container is: 1) run as Privileged OR 2) has CAP_SYS_ADMIN.
        # This could be enforced via PodSecurityPolicy
        name = "Containers should not run with allowPrivilegeEscalation"
        id = "CKV_K8S_20"
        # Location: container .securityContext.allowPrivilegeEscalation
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "securityContext" in conf:
            if "allowPrivilegeEscalation" in conf["securityContext"]:
                if conf["securityContext"]["allowPrivilegeEscalation"]:
                    return CheckResult.FAILED
            else:
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = AllowPrivilegeEscalation()
