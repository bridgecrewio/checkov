from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class PodSecurityContext(BaseResourceCheck):

    def __init__(self):
        # CIS-1.5 5.7.3
        name = "Apply security context to your pods and containers"
        # Security context can be set at pod or container level.
        id = "CKV_K8S_29"

        supported_resources = ['kubernetes_pod', 'kubernetes_deployment', 'kubernetes_daemonset']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "spec" not in conf:
            self.evaluated_keys = [""]
            return CheckResult.FAILED
        spec = conf['spec'][0]
        if spec.get("container"):
            containers = spec.get("container")

            for idx, container in enumerate(containers):
                if type(container) != dict:
                    return CheckResult.UNKNOWN

                if not container.get("security_context"):
                    self.evaluated_keys = ["spec/[0]/container/{idx}"]
                    return CheckResult.FAILED
            return CheckResult.PASSED

        if spec.get("template") and isinstance(spec.get("template"), list):
            template = spec.get("template")[0]
            if template.get("spec") and isinstance(template.get("spec"), list):
                temp_spec = template.get("spec")[0]
                if temp_spec.get("container"):
                    containers = temp_spec.get("container")

                    for idx, container in enumerate(containers):
                        if type(container) != dict:
                            return CheckResult.UNKNOWN

                        if not container.get("security_context"):
                            self.evaluated_keys = ["spec/[0]/template/[0]/spec/[0]/container/{idx}"]
                            return CheckResult.FAILED
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = PodSecurityContext()
