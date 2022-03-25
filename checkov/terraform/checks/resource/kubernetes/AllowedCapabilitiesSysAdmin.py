from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AllowedCapabilitiesSysAdmin(BaseResourceCheck):

    def __init__(self):
        name = "Do not use the CAP_SYS_ADMIN linux capability"
        # This provides the most privilege and is similar to root
        # https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
        id = "CKV_K8S_39"

        supported_resources = ['kubernetes_pod']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        spec = conf['spec'][0]
        if spec.get("container"):
            containers = spec.get("container")

            for idx, container in enumerate(containers):
                if type(container) != dict:
                    return CheckResult.UNKNOWN
                if container.get("security_context") and isinstance(container.get("security_context"), list):
                    context = container.get("security_context")[0]
                    if context.get("capabilities") and isinstance(context.get("capabilities"), list):
                        capabilities = context.get("capabilities")[0]
                        if capabilities.get("add") and isinstance(capabilities.get("add"), list):
                            add = capabilities.get("add")[0]
                            if "SYS_ADMIN" in add:
                                self.evaluated_keys = [f'spec/[0]/container/[{idx}]/'
                                                       f'security_context/[0]/capabilities/add']
                                return CheckResult.FAILED
        return CheckResult.PASSED


check = AllowedCapabilitiesSysAdmin()
