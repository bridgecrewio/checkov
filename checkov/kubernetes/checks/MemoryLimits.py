from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class MemoryLimits(BaseK8Check):

    def __init__(self):
        name = "Memory limits should be set"
        id = "CKV_K8S_13"
        # Location: container .resources.limits.memory
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return conf['parent']

    def scan_spec_conf(self, conf):
        if "resources" in conf:
            if "limits" in conf["resources"]:
                if "memory" not in conf["resources"]["limits"]:
                    return CheckResult.FAILED
            else:
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.PASSED

check = MemoryLimits()