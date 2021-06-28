from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class MinimizeCapabilities(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.2.9
        name = "Minimize the admission of containers with capabilities assigned"
        id = "CKV_K8S_37"
        # Location: container .securityContext.capabilities.drop
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if conf.get("securityContext"):
            if conf["securityContext"].get("capabilities"):
                if conf["securityContext"]["capabilities"].get("drop"):
                    for d in conf["securityContext"]["capabilities"]["drop"]:
                        if "ALL" in d:
                            return CheckResult.PASSED
        return CheckResult.FAILED


check = MinimizeCapabilities()
