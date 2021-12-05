from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check


class AllowedCapabilities(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.2.8
        name = "Do not allow containers with added capability"
        # No capabilities may be added beyond the default set
        # https://kubernetes.io/docs/concepts/policy/pod-security-policy/#capabilities
        # Location: PodSecurityPolicy.spec.allowedCapabilities
        id = "CKV_K8S_24"
        supported_kind = ['PodSecurityPolicy']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        if "spec" in conf:
            if "allowedCapabilities" in conf["spec"]:
                if conf["spec"]["allowedCapabilities"]:
                    return CheckResult.FAILED
        return CheckResult.PASSED

check = AllowedCapabilities()