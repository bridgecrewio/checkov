from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DropCapabilitiesPSP(BaseResourceCheck):

    def __init__(self):
        # CIS-1.3 1.7.7
        # CIS-1.5 5.2.7
        name = "Do not admit containers with the NET_RAW capability"
        # Location: PodSecurityPolicy.spec.requiredDropCapabilities
        id = "CKV_K8S_7"

        supported_resources = ['kubernetes_pod_security_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get('spec'):
            spec = conf.get('spec')[0]
            if not spec:
                return CheckResult.UNKNOWN

            if spec.get("required_drop_capabilities"):
                drop_cap = spec.get("required_drop_capabilities")[0]
                if drop_cap and isinstance(drop_cap, list):
                    if any(cap in drop_cap for cap in ("ALL", "NET_RAW")):
                        return CheckResult.PASSED

        return CheckResult.FAILED


check = DropCapabilitiesPSP()
