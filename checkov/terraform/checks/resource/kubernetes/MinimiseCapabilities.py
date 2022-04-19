from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class MinimiseCapabilities(BaseResourceCheck):

    def __init__(self):
        # CIS-1.5 5.2.9
        name = "Minimise the admission of containers with capabilities assigned"
        id = "CKV_K8S_37"

        supported_resources = ['kubernetes_pod']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf['spec'][0]
        if spec.get("container"):
            containers = spec.get("container")

            for idx, container in enumerate(containers):
                if not isinstance(container, dict):
                    return CheckResult.UNKNOWN
                if container.get("security_context"):
                    context = container.get("security_context")[0]
                    if context.get("capabilities"):
                        capabilities = context.get("capabilities")[0]
                        if capabilities.get("drop") and isinstance(capabilities.get("drop"), list):
                            drop = capabilities.get("drop")[0]
                            if not any(item in ("ALL", "all") for item in drop):
                                self.evaluated_keys = [f'spec/[0]/container/[{idx}]/'
                                                       f'security_context/[0]/capabilities/drop']
                                return CheckResult.FAILED
                        else:
                            self.evaluated_keys = [f'spec/[0]/container/[{idx}]/'
                                                   f'security_context/[0]/capabilities']
                            return CheckResult.FAILED
        return CheckResult.PASSED


check = MinimiseCapabilities()
