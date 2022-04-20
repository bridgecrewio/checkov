from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CPURequests(BaseResourceCheck):
    def __init__(self):
        name = "CPU requests should be set"
        id = "CKV_K8S_10"
        supported_resources = ["kubernetes_pod"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "spec" not in conf:
            self.evaluated_keys = [""]
            return CheckResult.FAILED
        spec = conf['spec'][0]

        containers = spec.get("container")
        for idx, container in enumerate(containers):
            if type(container) != dict:
                return CheckResult.UNKNOWN
            if container.get("resources"):
                resources = container.get("resources")[0]
                if resources.get('requests'):
                    limits = resources.get('requests')[0]
                    if limits.get('cpu'):
                        return CheckResult.PASSED
                    self.evaluated_keys = [f'spec/[0]/container/[{idx}]/resources/[0]/requests']
                    return CheckResult.FAILED
                self.evaluated_keys = [f'spec/[0]/container/[{idx}]/resources']
                return CheckResult.FAILED
            self.evaluated_keys = [f'spec/[0]/container/[{idx}]']
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CPURequests()
