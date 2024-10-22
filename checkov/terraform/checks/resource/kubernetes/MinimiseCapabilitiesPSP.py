from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class MinimiseCapabilitiesPSP(BaseResourceCheck):

    def __init__(self):
        # CIS-1.3 1.7.7
        # CIS-1.5 5.2.9
        name = "Minimise the admission of containers with capabilities assigned"
        # Location: PodSecurityPolicy.spec.requiredDropCapabilities
        id = "CKV_K8S_36"

        supported_resources = ['kubernetes_pod_security_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        self.evaluated_keys = [""]
        if conf.get('spec'):
            spec = conf.get('spec')[0]
            if not spec:
                return CheckResult.UNKNOWN

            self.evaluated_keys = ["spec"]
            if spec.get("required_drop_capabilities"):
                return CheckResult.PASSED

        return CheckResult.FAILED


check = MinimiseCapabilitiesPSP()
