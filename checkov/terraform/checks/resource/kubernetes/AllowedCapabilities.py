from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AllowedCapabilities(BaseResourceCheck):

    def __init__(self):
        # CIS-1.5 5.2.8
        name = "Minimize the admission of containers with added capability"
        # Do not generally permit containers with capabilities assigned beyond the default set
        # https://kubernetes.io/docs/concepts/policy/pod-security-policy/#capabilities

        id = "CKV_K8S_25"

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
                if container.get("security_context"):
                    context = container.get("security_context")[0]
                    if context.get("capabilities"):
                        capabilities = context.get("capabilities")[0]
                        if capabilities.get("add"):
                            add = capabilities.get("add")[0]
                            if add:
                                self.evaluated_keys = [f'spec/[0]/container/[{idx}]/'
                                                       f'security_context/[0]/capabilities/add']
                                return CheckResult.FAILED
        return CheckResult.PASSED


check = AllowedCapabilities()
