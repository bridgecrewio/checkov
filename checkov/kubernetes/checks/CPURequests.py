from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class CPURequests(BaseK8Check):

    def __init__(self):
        name = "CPU requests should be set"
        id = "CKV_K8S_10"
        # Location: container .resources.requests.cpu
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if conf.get("resources"):
            if "requests" in conf["resources"]:
                if "cpu" not in conf["resources"]["requests"]:
                    return CheckResult.FAILED
            else:
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CPURequests()
