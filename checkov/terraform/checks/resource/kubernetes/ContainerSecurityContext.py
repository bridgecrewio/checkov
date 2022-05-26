from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ContainerSecurityContext(BaseResourceCheck):

    def __init__(self):
        # CIS-1.5 5.7.3
        name = "Apply security context to your pods and containers"
        # Security context can be set at pod or container level.
        # Location: container .securityContext
        id = "CKV_K8S_30"

        supported_resources = ['kubernetes_pod']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf.get('spec', [None])[0]
        if isinstance(spec, dict) and spec.get("container"):
            containers = spec.get("container")

            for idx, container in enumerate(containers):
                if type(container) != dict:
                    return CheckResult.UNKNOWN
                if not container.get("security_context"):
                    self.evaluated_keys = [f'spec/[0]/container/[{idx}]/security_context']
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = ContainerSecurityContext()
