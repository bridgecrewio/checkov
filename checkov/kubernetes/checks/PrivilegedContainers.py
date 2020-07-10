from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class PrivilegedContainers(BaseK8Check):

    def __init__(self):
        # CIS-1.3 1.7.1
        # CIS-1.5 5.2.1
        name = "Container should not be privileged"
        id = "CKV_K8S_16"
        # Location: container .securityContext.privileged
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return conf['parent']

    def scan_spec_conf(self, conf):
        if "securityContext" in conf:
            if "privileged" in conf["securityContext"]:
                if conf["securityContext"]["privileged"]:
                    return CheckResult.FAILED
        return CheckResult.PASSED

check = PrivilegedContainers()