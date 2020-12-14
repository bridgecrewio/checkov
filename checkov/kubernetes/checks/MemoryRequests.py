from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class MemoryRequests(BaseK8Check):

    def __init__(self):
        name = "Memory requests should be set"
        id = "CKV_K8S_12"
        # Location: container .resources.requests.memory
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "resources" in conf:
            if "requests" in conf["resources"]:
                if "memory" not in conf["resources"]["requests"]:
                    return CheckResult.FAILED
            else:
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = MemoryRequests()
